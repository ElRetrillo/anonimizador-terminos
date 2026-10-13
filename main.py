import os
import re
import time
import uuid
import logging
from pathlib import Path
from typing import List, Optional

import pymupdf
from fastapi import FastAPI, Request, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from enterprise_recognizers import register_enterprise_spanish_recognizers, refine_and_translate_entities

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Anonimizador de Documentación Empresarial")

# Directorio dedicado para almacenamiento temporal de documentos procesados
BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "processed_docs"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Configurar soporte para múltiples idiomas (Inglés y Español) en Presidio
nlp_configuration = {
    "nlp_engine_name": "spacy",
    "models": [
        {"lang_code": "en", "model_name": "en_core_web_sm"},
        {"lang_code": "es", "model_name": "es_core_news_sm"},
    ],
}

provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
nlp_engine = provider.create_engine()

# Cargar motores de Presidio con soporte multilenguaje
analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en", "es"])
anonymizer = AnonymizerEngine()

# Registrar reconocedores empresariales y contractuales en español
register_enterprise_spanish_recognizers(analyzer)

# Montar plantillas HTML
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def cleanup_stale_files(max_age_seconds: int = 3600):
    """Elimina archivos en processed_docs con una antigüedad mayor a max_age_seconds."""
    now = time.time()
    try:
        for item in PROCESSED_DIR.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                try:
                    if now - item.stat().st_mtime > max_age_seconds:
                        item.unlink(missing_ok=True)
                except Exception as ex:
                    logger.warning(f"No se pudo limpiar archivo obsoleto {item.name}: {ex}")
    except Exception as e:
        logger.warning(f"Error durante limpieza periódica: {e}")


def remove_file_task(file_path: Path):
    """Tarea en segundo plano para eliminar un archivo inmediatamente tras ser descargado."""
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Archivo eliminado del sistema con éxito: {file_path.name}")
    except Exception as e:
        logger.error(f"Error al eliminar archivo tras descarga {file_path.name}: {e}")


class AnonymizeRequest(BaseModel):
    text: str
    language: Optional[str] = "es"
    entities: Optional[List[str]] = None


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/api/anonymize")
def process_anonymize(req: AnonymizeRequest):
    if not req.text.strip():
        return {
            "anonymized_text": "",
            "detected_entities": []
        }

    lang = req.language if req.language in ["en", "es"] else "es"

    # 1. Analizar texto con presidio-analyzer
    raw_results = analyzer.analyze(
        text=req.text,
        entities=req.entities if req.entities else None,
        language=lang
    )

    # 2. Desambiguar y traducir entidades a etiquetas en español
    results = refine_and_translate_entities(raw_results, req.text)

    # 3. Anonimizar texto con presidio-anonymizer
    anonymized_result = anonymizer.anonymize(
        text=req.text,
        analyzer_results=results
    )

    detected = [
        {
            "entity_type": res.entity_type,
            "start": res.start,
            "end": res.end,
            "score": round(res.score, 2),
            "text": req.text[res.start:res.end]
        }
        for res in results
    ]

    return {
        "anonymized_text": anonymized_result.text,
        "detected_entities": detected
    }


@app.post("/api/anonymize-pdf")
async def process_pdf(
    file: UploadFile = File(...),
    language: str = Form("es"),
    redaction_style: str = Form("label"),
    delete_after_download: bool = Form(True)
):
    """
    Recibe un documento PDF, extrae su texto, analiza datos sensibles con Presidio,
    aplica redacciones permanentes sobre las páginas del PDF y almacena el resultado
    en 'processed_docs/' con un identificador UUID libre de conflictos.
    """
    # Limpieza preventiva de archivos temporales antiguos (>1 hora)
    cleanup_stale_files(max_age_seconds=3600)

    # Validación básica de extensión
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="El archivo proporcionado debe tener formato PDF (.pdf)."
        )

    # Leer contenido del archivo
    content = await file.read()
    if not content or len(content) < 4:
        raise HTTPException(status_code=400, detail="El archivo subido está vacío.")

    # Validar cabecera PDF
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="El archivo no es un documento PDF válido.")

    lang = language if language in ["en", "es"] else "es"

    try:
        # Abrir documento con PyMuPDF
        doc = pymupdf.open(stream=content, filetype="pdf")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo interpretar el archivo PDF: {str(e)}")

    total_pages = len(doc)
    if total_pages == 0:
        doc.close()
        raise HTTPException(status_code=400, detail="El PDF no contiene páginas legibles.")

    detected_entities = []
    pages_summary = []
    total_extracted_chars = 0

    # Procesar página por página
    for page_idx in range(total_pages):
        page = doc[page_idx]
        page_num = page_idx + 1
        page_text = page.get_text()
        total_extracted_chars += len(page_text.strip())

        page_entities = []
        anon_page_text = page_text

        if page_text.strip():
            # 1. Analizar entidades con Presidio
            raw_results = analyzer.analyze(text=page_text, language=lang)

            # 2. Desambiguar y traducir entidades a etiquetas en español
            results = refine_and_translate_entities(raw_results, page_text)

            # 3. Obtener texto anonimizado
            anonymized_obj = anonymizer.anonymize(text=page_text, analyzer_results=results)
            anon_page_text = anonymized_obj.text

            # Rastrear rectángulos censurados en la página para evitar que se solapen tags
            page_redacted_boxes = []

            for res in results:
                raw_entity_text = page_text[res.start:res.end]
                clean_text = raw_entity_text.strip(" \t\r\n,;:.\"\'()[]{}")
                if not clean_text:
                    continue

                entity_info = {
                    "page": page_num,
                    "entity_type": res.entity_type,
                    "text": clean_text,
                    "score": round(res.score, 2),
                    "start": res.start,
                    "end": res.end
                }
                detected_entities.append(entity_info)
                page_entities.append(entity_info)

                # Buscar rectángulos de coincidencia en la página
                rects = page.search_for(
                    clean_text,
                    flags=pymupdf.TEXT_DEHYPHENATE | pymupdf.TEXT_PRESERVE_WHITESPACE
                )

                # Si tiene saltos de línea y no se encontró completo, buscar por líneas
                if not rects and "\n" in clean_text:
                    for line in clean_text.splitlines():
                        sub = line.strip(" \t\r\n,;:.\"\'()[]{}")
                        if len(sub) >= 2:
                            rects.extend(page.search_for(
                                sub,
                                flags=pymupdf.TEXT_DEHYPHENATE | pymupdf.TEXT_PRESERVE_WHITESPACE
                            ))

                # Filtrar rectángulos que solapen con una censura previa
                # para asegurar que SOLAMENTE aparezca un tag por dato visible en la página.
                valid_rects = []
                for r in rects:
                    collides = False
                    for prev_box in page_redacted_boxes:
                        inter = r & prev_box
                        if not inter.is_empty:
                            min_area = min(r.get_area(), prev_box.get_area())
                            if (min_area > 0 and (inter.get_area() / min_area) > 0.05) or inter.get_area() > 2.0:
                                collides = True
                                break
                    if not collides:
                        valid_rects.append(r)

                if not valid_rects:
                    continue

                # Determinar cuál rectángulo llevará la etiqueta visible (el más espacioso de la entidad)
                best_rect_idx = 0
                max_w = -1
                for idx, r in enumerate(valid_rects):
                    if r.width > max_w:
                        max_w = r.width
                        best_rect_idx = idx

                tag_label = f"[{res.entity_type}]" if redaction_style != "highlight" else f"<{res.entity_type}>"

                for idx, r in enumerate(valid_rects):
                    is_primary = (idx == best_rect_idx)
                    if redaction_style == "blackout" or not is_primary or r.width < 25:
                        annot_text = ""
                        font_sz = 6.5
                    else:
                        annot_text = tag_label
                        # Calcular tamaño de fuente dinámico para evitar desbordes y saltos de línea antiestéticos
                        char_len = len(annot_text)
                        max_char_width = (r.width - 4) / char_len if char_len > 0 else 6.5
                        font_sz = max(4.0, min(7.0, max_char_width / 0.52))

                    if redaction_style == "blackout":
                        page.add_redact_annot(
                            r,
                            text="",
                            fill=(0.0, 0.0, 0.0)
                        )
                    elif redaction_style == "highlight":
                        page.add_redact_annot(
                            r,
                            text=annot_text,
                            fill=(0.88, 0.90, 0.94),
                            text_color=(0.1, 0.1, 0.1),
                            fontsize=font_sz
                        )
                    else:
                        # Estilo "label" predeterminado: caja oscura con etiqueta formal
                        page.add_redact_annot(
                            r,
                            text=annot_text,
                            fill=(0.12, 0.15, 0.22),
                            text_color=(1.0, 1.0, 1.0),
                            fontsize=font_sz
                        )

                    page_redacted_boxes.append(r)

            # Aplicar redacciones criptográficas permanentes en la página
            page.apply_redactions()

        pages_summary.append({
            "page_number": page_num,
            "entities_found": len(page_entities),
            "anonymized_text": anon_page_text
        })

    # Advertencia si el PDF no contiene texto legible (ej. escaneo como imagen pura)
    has_text_layer = total_extracted_chars > 0

    # Generar nombre único para evitar colisiones
    safe_stem = re.sub(r'[^a-zA-Z0-9_\-]', '_', Path(file.filename).stem)[:40]
    file_uuid = uuid.uuid4().hex[:12]
    storage_filename = f"anon_{file_uuid}_{safe_stem}.pdf"
    output_path = PROCESSED_DIR / storage_filename

    # Guardar PDF anonimizado con recolección de basura para purgar datos
    try:
        doc.save(str(output_path), garbage=4, deflate=True)
    finally:
        doc.close()

    download_display_name = f"anonimizado_{safe_stem}.pdf"

    return {
        "success": True,
        "file_id": storage_filename,
        "download_name": download_display_name,
        "total_pages": total_pages,
        "total_entities": len(detected_entities),
        "has_text_layer": has_text_layer,
        "detected_entities": detected_entities,
        "pages_summary": pages_summary,
        "delete_after_download": delete_after_download,
        "message": "PDF procesado y anonimizado con éxito." if has_text_layer else "El documento fue procesado, pero no se encontró capa de texto digital legible (podría ser una imagen escaneada)."
    }


@app.get("/api/download-pdf/{file_id}")
async def download_pdf(
    file_id: str,
    delete_after: bool = True,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Descarga el archivo PDF anonimizado.
    Si delete_after es True, se programa la eliminación inmediata del archivo
    en segundo plano tras ser entregado al cliente.
    """
    # Prevenir ataques de Directory Traversal
    safe_name = Path(file_id).name
    target_path = (PROCESSED_DIR / safe_name).resolve()

    if target_path.parent != PROCESSED_DIR.resolve() or not target_path.exists():
        raise HTTPException(
            status_code=404,
            detail="El documento solicitado no existe o ya fue eliminado del servidor."
        )

    # Nombre amigable para descarga
    clean_download_name = re.sub(r'^anon_[a-f0-9]+_', 'anonimizado_', safe_name)
    if not clean_download_name.endswith(".pdf"):
        clean_download_name += ".pdf"

    if delete_after:
        background_tasks.add_task(remove_file_task, target_path)

    return FileResponse(
        path=str(target_path),
        filename=clean_download_name,
        media_type="application/pdf",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache"
        }
    )


@app.post("/api/cleanup-docs")
def cleanup_docs():
    """
    Elimina todos los archivos procesados de la carpeta local de forma inmediata.
    """
    deleted_count = 0
    try:
        for item in PROCESSED_DIR.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                try:
                    item.unlink(missing_ok=True)
                    deleted_count += 1
                except Exception as ex:
                    logger.warning(f"Error borrando {item.name}: {ex}")
        return {
            "success": True,
            "deleted_files": deleted_count,
            "message": f"Se eliminaron {deleted_count} archivo(s) del almacenamiento local."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el vaciado: {str(e)}")
