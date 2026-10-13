import re
from typing import List, Tuple
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult

def register_enterprise_spanish_recognizers(analyzer):
    """
    Registra reconocedores orientados a documentación corporativa y contractual en español
    con etiquetas formalizadas en español y alta capacidad de granularidad y desambiguación.
    """

    # =========================================================================
    # 1. IDENTIFICACIÓN Y TRIBUTACIÓN (RUT / DNI / PASAPORTE)
    # =========================================================================
    rut_patterns = [
        Pattern(name="cl_rut_standard", regex=r"\b(\d{1,2}(?:\.?\d{3}){2}-[\dkK])\b", score=0.98),
        Pattern(name="cl_rut_plain", regex=r"\b(\d{7,8}-[\dkK])\b", score=0.95)
    ]
    rut_recognizer = PatternRecognizer(
        supported_entity="RUT",
        patterns=rut_patterns,
        context=["rut", "run", "cédula", "identidad", "c.i.", "dni", "rol único tributario"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(rut_recognizer)

    id_pattern = Pattern(
        name="general_id_doc",
        regex=r"(?i)\b(?:pasaporte|c\.?i\.?|dni|c[eé]dula(?:\s+de\s+identidad)?)\s*(?:n[°º\.]?|n[uú]mero)?\s*[:#]?\s*([a-zA-Z0-9\.\-]{6,15})\b",
        score=0.92
    )
    id_recognizer = PatternRecognizer(
        supported_entity="DOCUMENTO_IDENTIDAD",
        patterns=[id_pattern],
        context=["documento", "identidad", "pasaporte", "cédula", "nacionalidad"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(id_recognizer)

    # =========================================================================
    # 2. PERSONAS (Fórmulas Legales y Contractuales en Español)
    # =========================================================================
    # Fórmulas de comparecencia legal: don/doña/señor/comparece Juan Pérez
    legal_name_pattern = Pattern(
        name="es_legal_person_formula",
        regex=r"\b(?:[dD]on|[dD]oña|[sS]r\.|[sS]ra\.|[sS]eñor|[sS]eñora|[cC]omparece|[aA]\s+nombre\s+de|[tT]rabajador|[pP]aciente)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ]+){1,4})\b",
        score=0.92
    )
    person_recognizer = PatternRecognizer(
        supported_entity="PERSONA",
        patterns=[legal_name_pattern],
        global_regex_flags=re.MULTILINE | re.DOTALL,
        supported_language="es"
    )
    analyzer.registry.add_recognizer(person_recognizer)

    # =========================================================================
    # 3. DIRECCIONES FÍSICAS (DOMICILIOS COMPLETOS Y PRECISOS)
    # =========================================================================
    address_patterns = [
        Pattern(
            name="es_address_street",
            regex=r"(?i)\b(?:avenida|avda\.?|av\.?|calle|pasaje|psje\.?|camino|paseo|boulevard|diagonal|carretera)\s+[a-záéíóúñA-ZÁÉÍÓÚÑ0-9\.\s'-]{3,45}\s*(?:n[°º\.]|número|#)?\s*\d{1,6}(?:\s*(?:depto|departamento|oficina|of\.?|piso|block|torre)\s*[\w\d]+)?\b",
            score=0.96
        ),
        Pattern(
            name="es_office_address",
            regex=r"(?i)\b(?:oficina|of\.?|departamento|depto\.?|piso)\s*(?:n[°º\.]|#)?\s*\d{1,5}(?:\s*,\s*(?:torre|edificio)\s*[\w\d\s]+)?\b",
            score=0.90
        )
    ]
    address_recognizer = PatternRecognizer(
        supported_entity="DIRECCION",
        patterns=address_patterns,
        context=["domiciliado", "domicilio", "residencia", "dirección", "ubicado en", "oficina central", "sede", "sucursal"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(address_recognizer)

    # UBICACION general (ciudades, comunas aisladas) se desactiva como entidad sensible independiente
    # para no censurar información geográfica general. Solo se reconoce si forma parte de una DIRECCION física.

    # =========================================================================
    # 4. EMPRESAS Y RAZONES SOCIALES (Estrictamente case-sensitive)
    # =========================================================================
    empresa_patterns = [
        # Sociedades con tipos societarios explícitos (SpA, S.A., Ltda, etc.)
        Pattern(
            name="es_empresa_societaria",
            regex=r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ0-9\.\'\-]{1,25}(?:\s+(?:[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ0-9\.\'\-]{1,25}|de(?:l)?|los|las|e|y)){0,4}\s+(?:SpA|S\.A\.|S\.A|Sociedad\s+Anónima|Ltda\.?|Limitada|E\.I\.R\.L\.?|EIRL|S\.A\.C\.?|LLC|Inc\.?|Corp\.?)\b",
            score=0.96
        ),
        # Empresas con prefijos societarios/comerciales
        Pattern(
            name="es_empresa_prefijo",
            regex=r"\b(?:[iI]nversiones|[cC]onstructora|[iI]nmobiliaria|[mM]inera|[sS]ociedad\s+[cC]omercial|[sS]ociedad\s+[cC]ontractual|[eE]mpresa|[cC]ompañía|[tT]ransportes|[aA]grícola)\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ0-9\.\'\-]{2,25}(?:\s+(?:de(?:l)?|los|las|y|e)?\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ0-9\.\'\-]{2,25}){0,3}(?:\s+(?:SpA|S\.A\.|Ltda\.?|Limitada|E\.I\.R\.L\.?))?\b",
            score=0.93
        )
    ]
    empresa_recognizer = PatternRecognizer(
        supported_entity="EMPRESA",
        patterns=empresa_patterns,
        global_regex_flags=re.MULTILINE | re.DOTALL,
        supported_language="es"
    )
    analyzer.registry.add_recognizer(empresa_recognizer)

    # =========================================================================
    # 5. ENTIDADES BANCARIAS Y FINANCIERAS (Diferenciadas de 'ORGANIZACION')
    # =========================================================================
    bancos_pattern = Pattern(
        name="es_entidad_bancaria",
        regex=r"(?i)\b(?:banco\s+(?:santander(?:\s+chile)?|de\s+chile|del\s+estado(?:\s+de\s+chile)?|estado|bci|itau|itaú(?:\s+corpbanca)?|scotiabank(?:\s+chile)?|falabella|ripley|security|bice|consorcio|internacional)|bci\s+banco|coopeuch|bancoestado)\b",
        score=0.96
    )
    banco_recognizer = PatternRecognizer(
        supported_entity="ENTIDAD_BANCARIA",
        patterns=[bancos_pattern],
        context=["banco", "transferencia", "depósito", "cuenta", "sucursal"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(banco_recognizer)

    # =========================================================================
    # 6. NOTARÍAS Y MINISTROS DE FE
    # =========================================================================
    notaria_pattern = Pattern(
        name="es_notaria",
        regex=r"(?i)\b(?:notar[ií]a\s+(?:p[uú]blica\s+)?(?:de\s+)?[a-záéíóúñA-ZÁÉÍÓÚÑ\s\.\'-]{3,35}|notario\s+p[uú]blico\s+[a-záéíóúñA-ZÁÉÍÓÚÑ\s\.\'-]{3,35})\b",
        score=0.94
    )
    notaria_recognizer = PatternRecognizer(
        supported_entity="NOTARIA",
        patterns=[notaria_pattern],
        context=["notaría", "notario", "escritura pública", "protocolo", "ante mí"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(notaria_recognizer)

    # =========================================================================
    # 7. INSTITUCIONES PÚBLICAS Y REGULATORIAS
    # =========================================================================
    institucion_pattern = Pattern(
        name="es_institucion_publica",
        regex=r"(?i)\b(?:servicio\s+de\s+impuestos\s+internos|sii|tesorer[ií]a\s+general(?:\s+de\s+la\s+rep[uú]blica)?|tgr|registro\s+civil(?:\s+e\s+identificaci[oó]n)?|conservador\s+de\s+bienes\s+ra[ií]ces|cbr|inspecci[oó]n\s+del\s+trabajo|direcci[oó]n\s+del\s+trabajo|municipalidad\s+de\s+[a-záéíóúñA-ZÁÉÍÓÚÑ\s]{3,25}|ministerio\s+de\s+[a-záéíóúñA-ZÁÉÍÓÚÑ\s]{3,30}|fonasa|isapre\s+[a-záéíóúñA-ZÁÉÍÓÚÑ]{3,20})\b",
        score=0.94
    )
    institucion_recognizer = PatternRecognizer(
        supported_entity="INSTITUCION_PUBLICA",
        patterns=[institucion_pattern],
        context=["institución", "repartición", "organismo", "tribunal", "ministerio"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(institucion_recognizer)

    # =========================================================================
    # 8. PROFESIONES, CARGOS Y ROLES LABORALES / CORPORATIVOS
    # =========================================================================
    professions_list = [
        # Títulos de ingeniería y ciencias aplicadas compuestos
        "ingeniero civil industrial", "ingeniera civil industrial",
        "ingeniero civil informático", "ingeniera civil informática",
        "ingeniero civil en computación", "ingeniera civil en computación",
        "ingeniero civil de minas", "ingeniera civil de minas",
        "ingeniero civil electrónico", "ingeniera civil electrónica",
        "ingeniero civil mecánico", "ingeniera civil mecánica",
        "ingeniero civil químico", "ingeniera civil química",
        "ingeniero civil", "ingeniera civil",
        "ingeniero comercial", "ingeniera comercial",
        "ingeniero industrial", "ingeniera industrial",
        "ingeniero informático", "ingeniera informática",
        "ingeniero en computación", "ingeniera en computación",
        "ingeniero en informática", "ingeniera en informática",
        "ingeniero de software", "ingeniera de software",
        "ingeniero de ejecución", "ingeniera de ejecución",
        "ingeniero agrónomo", "ingeniera agrónoma",
        "ingeniero constructor", "ingeniera constructora",
        "constructor civil", "constructora civil",
        "ingeniero", "ingeniera",
        # Ámbito legal y judicial
        "abogado defensor", "abogada defensora",
        "abogado laboral", "abogada laboral",
        "abogado corporativo", "abogada corporativa",
        "abogado", "abogada", "juez", "jueza", "fiscal",
        "defensor público", "defensora pública",
        # Ámbito financiero y contable
        "contador auditor", "contadora auditora",
        "contador general", "contadora general",
        "auditor externo", "auditora externa",
        "auditor interno", "auditora interna",
        "auditor", "auditora", "contador", "contadora",
        # Ámbito directivo y gerencial
        "gerente general", "gerenta general",
        "representante legal",
        "director ejecutivo", "directora ejecutiva",
        "director de operaciones", "directora de operaciones",
        "director de finanzas", "directora de finanzas",
        "gerente de finanzas", "gerenta de finanzas",
        "gerente de operaciones", "gerenta de operaciones",
        "gerente de administración y finanzas",
        "gerente de recursos humanos", "gerenta de recursos humanos",
        "gerente de informática", "gerenta de informática",
        "gerente comercial", "gerenta comercial",
        "gerente", "gerenta", "subgerente", "subgerenta",
        "apoderado especial", "apoderada especial",
        "apoderado", "apoderada",
        "presidente del directorio", "presidenta del directorio",
        "presidente", "presidenta",
        "secretario general", "secretaria general",
        "secretario", "secretaria",
        "administrador de empresas", "administradora de empresas",
        "administrador", "administradora",
        "socio fundador", "socia fundadora",
        "socio", "socia", "fundador", "fundadora",
        # Jefaturas y coordinación
        "jefe de proyecto", "jefa de proyecto",
        "jefe de operaciones", "jefa de operaciones",
        "jefe de área", "jefa de área",
        "jefe de sucursal", "jefa de sucursal",
        "coordinador general", "coordinadora general",
        "coordinador", "coordinadora",
        "supervisor", "supervisora",
        "ejecutivo de cuentas", "ejecutiva de cuentas",
        "ejecutivo comercial", "ejecutiva comercial",
        "ejecutivo", "ejecutiva",
        "asistente ejecutivo", "asistente ejecutiva",
        "asistente", "tesorero", "tesorera",
        # Ámbito salud y ciencias
        "médico cirujano", "médica cirujana",
        "médico general", "médica general",
        "médico", "médica",
        "cirujano dentista", "cirujana dentista",
        "odontólogo", "odontóloga",
        "enfermero universitario", "enfermera universitaria",
        "enfermero", "enfermera",
        "kinesiólogo", "kinesióloga",
        "químico farmacéutico", "química farmacéutica",
        "psicólogo clínico", "psicóloga clínica",
        "psicólogo", "psicóloga",
        "asistente social", "trabajador social", "trabajadora social",
        # Otras profesiones
        "arquitecto", "arquitecta",
        "periodista", "profesor", "profesora", "docente",
        "diseñador gráfico", "diseñadora gráfica",
        "diseñador", "diseñadora",
        "desarrollador de software", "desarrolladora de software",
        "desarrollador full stack", "desarrolladora full stack",
        "desarrollador", "desarrolladora",
        "programador", "programadora",
        "analista de sistemas", "analista programador", "analista",
        "consultor senior", "consultor", "consultora",
        "técnico en enfermería", "técnico en administración",
        "técnico", "técnica"
    ]
    # IMPORTANTE: Ordenar estrictamente de mayor a menor longitud
    professions_list.sort(key=len, reverse=True)
    professions_regex = r"(?i)\b(?:" + "|".join([re.escape(p) for p in professions_list]) + r")\b"
    profession_pattern = Pattern(name="es_profession_pattern", regex=professions_regex, score=0.92)
    profession_recognizer = PatternRecognizer(
        supported_entity="CARGO_O_PROFESION",
        patterns=[profession_pattern],
        context=["de profesión", "profesión", "oficio", "cargo", "en su calidad de", "representante", "actuando como", "titulado de"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(profession_recognizer)

    # =========================================================================
    # 9. EDAD Y ESTADO CIVIL
    # =========================================================================
    age_patterns = [
        Pattern(name="es_age_natural", regex=r"(?i)\b(?:tiene\s+|cumpli[oó]\s+|de\s+)?(\d{1,3})\s+a[ñn]os(?:\s+de\s+edad)?\b", score=0.92),
        Pattern(name="es_age_context", regex=r"(?i)\b(?:edad|edad:)\s*(\d{1,3})\b", score=0.88),
        Pattern(name="es_mayor_edad", regex=r"(?i)\b(?:mayor\s+de\s+edad|menor\s+de\s+edad)\b", score=0.88)
    ]
    age_recognizer = PatternRecognizer(
        supported_entity="EDAD",
        patterns=age_patterns,
        context=["edad", "cumplió", "años", "nacido", "mayoría de edad"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(age_recognizer)

    marital_status_list = ["soltero", "soltera", "casado", "casada", "viudo", "viuda", "divorciado", "divorciada", "conviviente civil"]
    marital_regex = r"(?i)\b(?:" + "|".join(marital_status_list) + r")\b"
    marital_pattern = Pattern(name="es_marital_pattern", regex=marital_regex, score=0.88)
    marital_recognizer = PatternRecognizer(
        supported_entity="ESTADO_CIVIL",
        patterns=[marital_pattern],
        context=["estado civil", "de estado civil"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(marital_recognizer)

    # =========================================================================
    # 10. DATOS BANCARIOS Y FINANCIEROS (CUENTAS, MONTOS)
    # =========================================================================
    bank_account_pattern = Pattern(
        name="es_bank_account",
        regex=r"(?i)\b(?:cta\.?\s*cte\.?|cuenta\s+corriente|cuenta\s+vista|cuenta\s+rut|cuenta\s+de\s+ahorro|cta\.?\s*vista)(?:\s+(?:del?|en|de\s+la)?\s+[a-záéíóúñA-ZÁÉÍÓÚÑ\s]{2,25})?\s*(?:n[°º\.]|número|#)?\s*[:#]?\s*(\d{5,18})\b",
        score=0.95
    )
    bank_recognizer = PatternRecognizer(
        supported_entity="CUENTA_BANCARIA",
        patterns=[bank_account_pattern],
        context=["banco", "depósito", "transferencia", "santander", "banco de chile", "bci", "scotiabank", "bancoestado", "itau"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(bank_recognizer)

    monetary_pattern = Pattern(
        name="es_monetary_amount",
        regex=r"(?i)(?:(?<=[\s\(\[])|^)(?:[\$]|clp|uf|usd|eur)\s*[\d\.,]{1,15}(?:\s*(?:pesos|dólares|uf|unidades\s+de\s+fomento))?\b",
        score=0.90
    )
    monetary_recognizer = PatternRecognizer(
        supported_entity="MONTO_FINANCIERO",
        patterns=[monetary_pattern],
        context=["pago", "sueldo", "remuneración", "monto", "honorarios", "precio", "suma de", "equivalente a"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(monetary_recognizer)

    # =========================================================================
    # 11. TELÉFONOS EN FORMATO CHILENO / HISPANO
    # =========================================================================
    cl_phone_patterns = [
        Pattern(name="cl_phone_mobile", regex=r"(?i)(?:\+?56\s*9|\b9)\s*\d{4}\s*\d{4}\b", score=0.90),
        Pattern(name="cl_phone_landline", regex=r"(?i)(?:\+?56\s*[2-9]|\b[2-9])\s*\d{3,4}\s*\d{4}\b", score=0.85)
    ]
    phone_recognizer = PatternRecognizer(
        supported_entity="TELEFONO",
        patterns=cl_phone_patterns,
        context=["teléfono", "fono", "celular", "móvil", "contacto", "whatsapp"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(phone_recognizer)

    # =========================================================================
    # 12. NACIONALIDAD Y FECHAS CONTRACTUALES
    # =========================================================================
    nationality_pattern = Pattern(
        name="es_nacionalidad",
        regex=r"(?i)\b(?:nacionalidad\s+(?:chilena|extranjera|argentina|peruana|colombiana|venezolana|española)|de\s+nacionalidad\s+[a-záéíóúñ]{4,15}|ciudadano\s+[a-záéíóúñ]{4,15})\b",
        score=0.88
    )
    nationality_recognizer = PatternRecognizer(
        supported_entity="NACIONALIDAD",
        patterns=[nationality_pattern],
        context=["nacionalidad", "ciudadano", "origen"],
        supported_language="es"
    )
    analyzer.registry.add_recognizer(nationality_recognizer)

    # FECHA se omite como entidad sensible por defecto para no censurar fechas contractuales o de calendario comunes.


# =============================================================================
# MAPEO Y MOTOR DE REFINAMIENTO Y DESAMBIGUACIÓN DE ENTIDADES EN ESPAÑOL
# =============================================================================

TRANSLATION_TABLE = {
    "PERSON": "PERSONA",
    "CL_RUT": "RUT",
    "ID_DOCUMENT": "DOCUMENTO_IDENTIDAD",
    "LOCATION": "UBICACION",
    "ORGANIZATION": "ORGANIZACION",
    "PHONE_NUMBER": "TELEFONO",
    "EMAIL_ADDRESS": "CORREO_ELECTRONICO",
    "IBAN_CODE": "CUENTA_BANCARIA",
    "FINANCIAL_AMOUNT": "MONTO_FINANCIERO",
    "PROFESSION": "CARGO_O_PROFESION",
    "MARITAL_STATUS": "ESTADO_CIVIL",
    "AGE": "EDAD",
    "DATE_TIME": "FECHA",
    "URL": "SITIO_WEB",
    "IP_ADDRESS": "DIRECCION_IP",
    "NRP": "NACIONALIDAD"
}

# Pesos de especificidad para resolución estricta de conflictos (Mayor gana)
PRIORITY_WEIGHTS = {
    "RUT": 100,
    "CUENTA_BANCARIA": 96,
    "ENTIDAD_BANCARIA": 95,
    "DOCUMENTO_IDENTIDAD": 95,
    "MONTO_FINANCIERO": 94,
    "TELEFONO": 93,
    "CORREO_ELECTRONICO": 93,
    "NOTARIA": 92,
    "INSTITUCION_PUBLICA": 92,
    "EMPRESA": 91,
    "DIRECCION": 90,
    "CARGO_O_PROFESION": 89,
    "ESTADO_CIVIL": 88,
    "EDAD": 88,
    "PERSONA": 85,
    "FECHA": 85,
    "NACIONALIDAD": 84,
    "UBICACION": 70,       # Las ciudades/comunas ceden ante direcciones completas o empresas
    "ORGANIZACION": 65,    # Organizaciones genéricas ceden ante empresas o bancos
    "SITIO_WEB": 60,       # URLs ceden ante correos electrónicos
}

BANK_KEYWORDS = [
    "banco", "santander", "bci", "scotiabank", "bancoestado", "itau", "itaú",
    "falabella", "ripley", "security", "bice", "consorcio", "coopeuch", "tenpo", "mach"
]

CORPORATE_PATTERNS = [
    "spa", "s.a.", "s.a", "ltda", "limitada", "eirl", "e.i.r.l", "inversiones",
    "constructora", "inmobiliaria", "minera", "sociedad", "compañía", "transporte"
]

NOTARY_KEYWORDS = ["notar", "notario", "notaría"]

PUBLIC_KEYWORDS = [
    "impuestos internos", "sii", "tesorería", "tesoreria", "tgr", "registro civil",
    "conservador", "cbr", "municipalidad", "ministerio", "inspección del trabajo", "fonasa"
]

STREET_PREFIXES = [
    "calle", "pasaje", "psje", "avenida", "avda", "av.", "camino", "paseo",
    "depto", "departamento", "oficina", "of.", "piso", "torre", "edificio",
    "boulevard", "diagonal", "carretera"
]

DOCUMENT_HEADERS = [
    "contrato", "prestacion de servicios", "prestación de servicios",
    "poder notarial", "escritura publica", "escritura pública", "escritura",
    "publica", "pública", "comparecencia", "finiquito", "anexo", "acuerdo",
    "declaracion jurada", "declaración jurada", "documento", "clausula",
    "cláusula", "estatuto", "minuta", "acta", "cédula de identidad", "cedula de identidad",
    "cédula", "cedula", "rol único tributario", "rol unico tributario", "identidad",
    "pasaporte", "documento de identidad"
]

ID_PREFIX_FILTER_REGEX = re.compile(
    r"^(?:(?:con\s+|en\s+)?(?:c[eé]dula(?:\s+nacional)?(?:\s+de\s+identidad)?|c\.?i\.?|dni|r\.?u\.?t\.?|run|pasaporte|rol\s+[uú]nico\s+tributario)\s*(?:n[°º\.]|n[uú]mero|#)?)\s*$",
    re.IGNORECASE
)

COMUNA_OR_LOCALITY_CONNECTOR = re.compile(
    r"^[\s,]+(?:comuna\s+de\s+|ciudad\s+de\s+|provincia\s+de\s+|regi[oó]n\s+de\s+|sector\s+de\s+|sector\s+|en\s+|de\s+)?",
    re.IGNORECASE
)

LEADING_NOISE_REGEX = re.compile(
    r"^(?:(?:[dD]on|[dD]oña|[sS]r\.|[sS]ra\.|[sS]eñor|[sS]eñora|[cC]omparece|[aA]\s+nombre\s+de|[tT]rabajador|[pP]aciente|[pP]ara\s+la\s+empresa|[pP]ara\s+el|[pP]ara\s+la|[pP]ara|[eE]n\s+la|[eE]n\s+el|[eE]n|[dD]e\s+la|[dD]el|[dD]e|[cC]on\s+domicilio\s+en|[dD]omiciliado\s+en|[cC]on)\s+)+",
    re.UNICODE
)


def trim_entity_boundaries(text: str, start: int, end: int, entity_type: str) -> Tuple[int, int]:
    """
    Pule los límites del span para aislar estrictamente el dato sensible,
    eliminando preposiciones, artículos y conectores gramaticales iniciales o signos finales.
    """
    sub = text[start:end]

    # No recortar preposiciones constitutivas (ej. 'Santiago de Chile' o 'Banco de Chile')
    if entity_type not in ["UBICACION", "ENTIDAD_BANCARIA", "NOTARIA", "INSTITUCION_PUBLICA"]:
        m = LEADING_NOISE_REGEX.match(sub)
        if m:
            start += m.end()

    # Purgar puntuación y espacios en extremos
    while end > start and text[end - 1] in " \t\r\n,;:.\"\'()[]{}":
        end -= 1
    while start < end and text[start] in " \t\r\n,;:.\"\'()[]{}":
        start += 1

    return start, end


def refine_and_translate_entities(raw_results: List[RecognizerResult], text: str) -> List[RecognizerResult]:
    """
    1. Traduce etiquetas estándar en inglés a español formal (ej. PERSON -> PERSONA).
    2. Pule límites exactos y descarta falsos positivos en encabezados/prefijos documentales.
    3. Desambigua entidades genéricas (ORGANIZACION/UBICACION -> EMPRESA, ENTIDAD_BANCARIA, DIRECCION, etc.).
    4. Consolida campos contiguos (ej. DIRECCION + Comuna/Ciudad -> 1 sola DIRECCION).
    5. Garantiza ESTRICTAMENTE que SOLO aparezca 1 TAG por dato sensible visible mediante
       resolución determinista de intervalos libres de solapamiento.
    """
    if not raw_results:
        return []

    # 1. Normalizar etiquetas al español, pulir límites y descartar prefijos espurios
    candidates = []
    for r in raw_results:
        ent = TRANSLATION_TABLE.get(r.entity_type, r.entity_type)
        
        # Limpiar límites del span
        clean_start, clean_end = trim_entity_boundaries(text, r.start, r.end, ent)
        if clean_start >= clean_end:
            continue

        val = text[clean_start:clean_end].strip(" \t\r\n,;:.\"\'()[]{}")
        if not val:
            continue

        # Descartar falsos positivos donde SpaCy o patrones etiquetan solo el rótulo del documento (ej. 'Cédula de Identidad N°')
        if ID_PREFIX_FILTER_REGEX.match(val):
            continue

        candidates.append(RecognizerResult(
            entity_type=ent,
            start=clean_start,
            end=clean_end,
            score=r.score
        ))

    # 2. Filtrar sub-solapamientos específicos (ej. SITIO_WEB dentro de CORREO_ELECTRONICO)
    email_ranges = [(r.start, r.end) for r in candidates if r.entity_type == "CORREO_ELECTRONICO"]
    filtered = []
    for r in candidates:
        if r.entity_type == "SITIO_WEB":
            in_email = any(em_start <= r.start and r.end <= em_end for em_start, em_end in email_ranges)
            if in_email:
                continue
        filtered.append(r)

    # 3. Desambiguación y clasificación fina
    refined = []
    for r in filtered:
        entity_slice = text[r.start:r.end].strip()
        lower_slice = entity_slice.lower()
        curr_type = r.entity_type
        curr_score = r.score

        # Descartar falsos positivos en títulos de documentos legales
        if curr_type in ["UBICACION", "ORGANIZACION", "PERSONA", "EMPRESA"]:
            if any(lower_slice.startswith(h) or lower_slice == h for h in DOCUMENT_HEADERS):
                continue

        # Desambiguación de 'ORGANIZACION'
        if curr_type == "ORGANIZACION":
            if any(b in lower_slice for b in BANK_KEYWORDS):
                curr_type = "ENTIDAD_BANCARIA"
                curr_score = max(curr_score, 0.95)
            elif any(c in lower_slice for c in CORPORATE_PATTERNS):
                curr_type = "EMPRESA"
                curr_score = max(curr_score, 0.94)
            elif any(n in lower_slice for n in NOTARY_KEYWORDS):
                curr_type = "NOTARIA"
                curr_score = max(curr_score, 0.94)
            elif any(p in lower_slice for p in PUBLIC_KEYWORDS):
                curr_type = "INSTITUCION_PUBLICA"
                curr_score = max(curr_score, 0.94)

        # Desambiguación de 'UBICACION'
        elif curr_type == "UBICACION":
            if any(lower_slice.startswith(prefix) or f" {prefix} " in f" {lower_slice} " for prefix in STREET_PREFIXES):
                curr_type = "DIRECCION"
                curr_score = max(curr_score, 0.94)
            elif any(c in lower_slice for c in CORPORATE_PATTERNS):
                curr_type = "EMPRESA"
                curr_score = max(curr_score, 0.93)
            elif any(n in lower_slice for n in NOTARY_KEYWORDS):
                curr_type = "NOTARIA"
                curr_score = max(curr_score, 0.93)
            elif any(b in lower_slice for b in BANK_KEYWORDS):
                curr_type = "ENTIDAD_BANCARIA"
                curr_score = max(curr_score, 0.95)

        refined.append(RecognizerResult(
            entity_type=curr_type,
            start=r.start,
            end=r.end,
            score=curr_score
        ))

    # 4. CONSOLIDACIÓN DE CAMPOS COMPUESTOS CONTIGUOS (DIRECCION + COMUNA/LOCALIDAD)
    # Si una DIRECCION está seguida o precedida por una UBICACION (ej. calle X 123 + , comuna de Y)
    # pertenecen al MISMO campo visible de domicilio, por lo que se consolidan en 1 solo tag DIRECCION.
    refined.sort(key=lambda x: x.start)
    consolidated: List[RecognizerResult] = []
    skip_indices = set()
    for i, r in enumerate(refined):
        if i in skip_indices:
            continue
        if r.entity_type == "DIRECCION":
            curr_start = r.start
            curr_end = r.end
            curr_score = r.score
            for j in range(i + 1, len(refined)):
                nxt = refined[j]
                if nxt.start >= curr_end:
                    gap = text[curr_end:nxt.start]
                    # Si el espacio entre entidades es solo un conector de dirección (coma, espacio, comuna de, etc.)
                    if nxt.entity_type in ["UBICACION", "DIRECCION"] and COMUNA_OR_LOCALITY_CONNECTOR.match(gap) and len(gap) <= 25:
                        curr_end = nxt.end
                        curr_score = max(curr_score, nxt.score)
                        skip_indices.add(j)
                    else:
                        break
            consolidated.append(RecognizerResult(
                entity_type="DIRECCION",
                start=curr_start,
                end=curr_end,
                score=curr_score
            ))
        else:
            consolidated.append(r)

    # 5. RESOLUCIÓN ESTRICTA DE SOLAPAMIENTOS: EXACTAMENTE 1 TAG POR DATO SENSIBLE
    # Ordenamos candidatos por:
    #   1° Prioridad semántica (especificidad del campo)
    #   2° Score de confianza
    #   3° Longitud de cobertura (mayor longitud gana en entidades compuestas)
    #   4° Posición de inicio
    consolidated.sort(key=lambda r: (
        -PRIORITY_WEIGHTS.get(r.entity_type, 50),
        -r.score,
        -(r.end - r.start),
        r.start
    ))

    # Filtrar entidades irrelevantes (ciudades/países aislados como 'Santiago' o 'Chile', y fechas comunes)
    # para no sobre-censurar el documento. Solo se censuran datos críticos y direcciones específicas.
    IGNORABLE_ENTITIES = {"UBICACION", "FECHA"}

    accepted_results: List[RecognizerResult] = []
    for cand in consolidated:
        if cand.entity_type in IGNORABLE_ENTITIES:
            continue

        # Condición de no solapamiento estricto: [cand.start, cand.end) no puede intersecar ningún [acc.start, acc.end)
        has_overlap = False
        for acc in accepted_results:
            if max(cand.start, acc.start) < min(cand.end, acc.end):
                has_overlap = True
                break

        if not has_overlap:
            accepted_results.append(cand)

    # Ordenar cronológicamente para el anonimizador
    accepted_results.sort(key=lambda x: x.start)
    return accepted_results
