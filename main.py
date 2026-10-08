from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

app = FastAPI(title="Presidio Demo App")

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

from enterprise_recognizers import register_enterprise_spanish_recognizers

# Registrar reconocedores empresariales y contractuales en español
register_enterprise_spanish_recognizers(analyzer)

# Montar plantillas HTML
templates = Jinja2Templates(directory="templates")

class AnonymizeRequest(BaseModel):
    text: str
    language: Optional[str] = "en"
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

    # 1. Analizar texto con presidio-analyzer
    results = analyzer.analyze(
        text=req.text,
        entities=req.entities if req.entities else None,
        language=req.language
    )

    # 2. Anonimizar texto con presidio-anonymizer
    anonymized_result = anonymizer.anonymize(
        text=req.text,
        analyzer_results=results
    )

    # Formatear entidades detectadas para mostrarlas
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
