import re
from presidio_analyzer import Pattern, PatternRecognizer

def register_enterprise_spanish_recognizers(analyzer):
    """
    Registra reconocedores orientados a documentación corporativa y contractual en español.
    """

    # =========================================================================
    # 1. IDENTIFICACIÓN Y TRIBUTACIÓN (RUT / DNI / PASAPORTE)
    # =========================================================================
    # RUT Chileno (con o sin puntos, con o sin guión, y soporte para dígito verificador K)
    rut_patterns = [
        Pattern(name="cl_rut_standard", regex=r"\b(\d{1,2}(?:\.?\d{3}){2}-[\dkK])\b", score=0.95),
        Pattern(name="cl_rut_plain", regex=r"\b(\d{7,8}-[\dkK])\b", score=0.90)
    ]
    rut_recognizer = PatternRecognizer(
        supported_entity="CL_RUT",
        patterns=rut_patterns,
        context=["rut", "run", "cédula", "identidad", "c.i.", "dni", "rol único tributario"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(rut_recognizer)

    # Documento de Identidad genérico / DNI / Pasaporte
    id_pattern = Pattern(name="general_id_doc", regex=r"(?i)\b(?:pasaporte|c\.?i\.?|dni|cédula\s+de\s+identidad)\s*(?:n[°º\.]?|número)?\s*([a-zA-Z0-9\.\-]{6,15})\b", score=0.85)
    id_recognizer = PatternRecognizer(
        supported_entity="ID_DOCUMENT",
        patterns=[id_pattern],
        context=["documento", "identidad", "pasaporte", "cédula", "nacionalidad"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(id_recognizer)

    # =========================================================================
    # 2. DIRECCIONES Y UBICACIONES (DOMICILIOS EMPRESARIALES Y PARTICULARES)
    # =========================================================================
    # Pasaje, Calle, Avenida, Camino, Oficina, Depto, Edificio, Manzana, etc.
    address_patterns = [
        Pattern(
            name="es_address_street",
            regex=r"(?i)\b(?:avenida|avda\.?|av\.?|calle|pasaje|psje\.?|camino|paseo|boulevard|diagonal|carretera)\s+[a-záéíóúñA-ZÁÉÍÓÚÑ0-9\.\s'-]{3,40}\s*(?:n[°º\.]|número|#)?\s*\d{1,6}(?:\s*(?:depto|departamento|oficina|of\.?|piso|block|torre)\s*[\w\d]+)?\b",
            score=0.90
        ),
        Pattern(
            name="es_office_address",
            regex=r"(?i)\b(?:oficina|of\.?|departamento|depto\.?|piso)\s*(?:n[°º\.]|#)?\s*\d{1,5}(?:\s*,\s*(?:torre|edificio)\s*[\w\d\s]+)?\b",
            score=0.85
        )
    ]
    address_recognizer = PatternRecognizer(
        supported_entity="LOCATION",
        patterns=address_patterns,
        context=["domiciliado", "domicilio", "residencia", "dirección", "ubicado en", "oficina central", "sede", "sucursal"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(address_recognizer)

    # Regiones / Comunas / Ciudades frecuentes en contratos chilenos e hispanos
    comuna_context_pattern = Pattern(
        name="es_comuna_pattern",
        regex=r"(?i)\b(?:comuna\s+de|ciudad\s+de|provincia\s+de|región\s+de)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]{3,25})\b",
        score=0.85
    )
    comuna_recognizer = PatternRecognizer(
        supported_entity="LOCATION",
        patterns=[comuna_context_pattern],
        context=["comuna", "ciudad", "provincia", "región", "jurisdicción"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(comuna_recognizer)

    # =========================================================================
    # 3. PROFESIONES, CARGOS Y ROLES LABORALES / CORPORATIVOS
    # =========================================================================
    professions_list = [
        "abogado", "abogada", "ingeniero", "ingeniera", "médico", "médica",
        "contador", "contadora", "auditor", "auditora", "arquitecto", "arquitecta",
        "psicólogo", "psicóloga", "periodista", "profesor", "profesora",
        "técnico", "técnica", "analista", "desarrollador", "desarrolladora",
        "programador", "programadora", "consultor", "consultora", "director", "directora",
        "gerente general", "gerente", "subgerente", "representante legal", "apoderado",
        "apoderada", "presidente", "presidenta", "secretario", "secretaria",
        "administrador", "administradora", "socio", "socia", "fundador", "fundadora",
        "jefe de proyecto", "ejecutivo", "ejecutiva", "jefe de operaciones"
    ]
    professions_regex = r"(?i)\b(?:" + "|".join([re.escape(p) for p in professions_list]) + r")\b"
    profession_pattern = Pattern(name="es_profession_pattern", regex=professions_regex, score=0.85)

    profession_recognizer = PatternRecognizer(
        supported_entity="PROFESSION",
        patterns=[profession_pattern],
        context=["de profesión", "profesión", "oficio", "cargo", "en su calidad de", "representante", "actuando como", "titulado de"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(profession_recognizer)

    # =========================================================================
    # 4. EDAD Y ESTADO CIVIL (Datos sensibles comunes en contratos/legales)
    # =========================================================================
    age_patterns = [
        Pattern(name="es_age_natural", regex=r"(?i)\b(?:tiene\s+|cumplió\s+)?(\d{1,3})\s+años(?:\s+de\s+edad)?\b", score=0.90),
        Pattern(name="es_age_context", regex=r"(?i)\b(?:edad|edad:)\s*(\d{1,3})\b", score=0.85),
        Pattern(name="es_mayor_edad", regex=r"(?i)\b(?:mayor\s+de\s+edad|menor\s+de\s+edad)\b", score=0.85)
    ]
    age_recognizer = PatternRecognizer(
        supported_entity="AGE",
        patterns=age_patterns,
        context=["edad", "cumplió", "años", "nacido", "mayoría de edad"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(age_recognizer)

    marital_status_list = ["soltero", "soltera", "casado", "casada", "viudo", "viuda", "divorciado", "divorciada", "conviviente civil"]
    marital_regex = r"(?i)\b(?:" + "|".join(marital_status_list) + r")\b"
    marital_pattern = Pattern(name="es_marital_pattern", regex=marital_regex, score=0.85)
    marital_recognizer = PatternRecognizer(
        supported_entity="MARITAL_STATUS",
        patterns=[marital_pattern],
        context=["estado civil", "de estado civil"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(marital_recognizer)

    # =========================================================================
    # 5. DATOS BANCARIOS Y FINANCIEROS (CUENTAS, TRANSFERENCIAS)
    # =========================================================================
    bank_account_pattern = Pattern(
        name="es_bank_account",
        regex=r"(?i)\b(?:cta\.?\s*cte\.?|cuenta\s+corriente|cuenta\s+vista|cuenta\s+rut|cuenta\s+de\s+ahorro|cta\.?\s*vista)\s*(?:n[°º\.]|número)?\s*[:#]?\s*(\d{5,16})\b",
        score=0.90
    )
    bank_recognizer = PatternRecognizer(
        supported_entity="IBAN_CODE",
        patterns=[bank_account_pattern],
        context=["banco", "depósito", "transferencia", "santander", "banco de chile", "bci", "scotiabank", "bancoestado", "itau"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(bank_recognizer)

    # Montos en Pesos Chilenos / Dólares / UF (Valores contractuales sensibles)
    monetary_pattern = Pattern(
        name="es_monetary_amount",
        regex=r"(?i)\b(?:\$|clp|uf|usd|eur)\s*[\d\.,]{1,15}(?:\s*(?:pesos|dólares|uf|unidades\s+de\s+fomento))?\b",
        score=0.80
    )
    monetary_recognizer = PatternRecognizer(
        supported_entity="FINANCIAL_AMOUNT",
        patterns=[monetary_pattern],
        context=["pago", "sueldo", "remuneración", "monto", "honorarios", "precio", "suma de", "equivalente a"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(monetary_recognizer)

    # =========================================================================
    # 6. TELÉFONOS EN FORMATO CHILENO / HISPANO
    # =========================================================================
    cl_phone_patterns = [
        Pattern(name="cl_phone_mobile", regex=r"(?i)(?:\+?56\s*9|\b9)\s*\d{4}\s*\d{4}\b", score=0.85),
        Pattern(name="cl_phone_landline", regex=r"(?i)(?:\+?56\s*[2-9]|\b[2-9])\s*\d{3,4}\s*\d{4}\b", score=0.80)
    ]
    phone_recognizer = PatternRecognizer(
        supported_entity="PHONE_NUMBER",
        patterns=cl_phone_patterns,
        context=["teléfono", "fono", "celular", "móvil", "contacto", "whatsapp"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(phone_recognizer)
