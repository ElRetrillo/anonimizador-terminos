# anonimizador-terminos

Herramienta basada en Microsoft Presidio (Presidio Analyzer y Presidio Anonymizer) orientada a la detección y anonimización de datos personales sensibles (PII) en documentación empresarial, contratos y escrituras en idioma español e inglés.

El sistema se ejecuta completamente en un contenedor Docker con modelos de lenguaje spaCy y reconocedores personalizados integrados.

---

## Requisitos Previos

- Docker Desktop (Windows / Mac) o Docker Engine (Linux).
- Git (opcional, para clonar el repositorio).

---

## Instalacion y Despliegue Rapido

1. Clonar el repositorio o ingresar al directorio del proyecto:
   ```bash
   git clone https://github.com/ElRetrillo/anonimizador-terminos.git
   cd anonimizador-terminos
   ```

2. Construir la imagen e iniciar el contenedor:
   ```bash
   docker compose up --build
   ```

3. Abrir en el navegador:
   http://localhost:8000

---

## Entidades Detectadas y Anonimizadas

El motor cuenta con reconocedores entrenados y adaptados para terminologia legal y contractual en espanol:

- <CL_RUT>: RUT chileno con o sin puntos, guion y digito verificador numerico o K (ej. 21.453.124-0).
- <ID_DOCUMENT>: Cedulas de identidad, DNI y pasaportes.
- <PERSON>: Nombres y apellidos completos identificados por el modelo de procesamiento de lenguaje natural en espanol.
- <LOCATION>: Domicilios comerciales y particulares (calles, avenidas, pasajes, numeros de domicilio, departamentos, oficinas, comunas y regiones).
- <PROFESSION>: Profesiones, oficios y cargos directivos (abogado, ingeniero, gerente general, representante legal, contador, etc.).
- <AGE>: Expresiones de edad en lenguaje natural (ej. "de 21 anos", "tiene 35 anos", "edad: 40").
- <MARITAL_STATUS>: Estado civil (soltero/a, casado/a, divorciado/a, viudo/a, conviviente civil).
- <IBAN_CODE>: Cuentas bancarias corrientes, vistas y cuentas de ahorro asociadas a entidades bancarias.
- <FINANCIAL_AMOUNT>: Montos, honorarios, remuneraciones y pagos en CLP, UF, USD.
- <PHONE_NUMBER>: Numeros telefonicos fijos y moviles chilenos e internacionales.
- <EMAIL_ADDRESS>: Direcciones de correo electronico.

---

## Caracteristicas de la Interfaz Web

- Diseno rectangular sobrio orientado a entornos corporativos.
- Selector de modo claro y modo oscuro para la visualizacion.
- Plantillas de prueba integradas (Contrato Laboral, Poder Notarial, Pagos/Finanzas).
- Visualizacion en tiempo real de las entidades detectadas con desglose del tipo y nivel de confianza.
- Boton de copiado directo del texto anonimizado al portapapeles.

---

## Ejecucion de Pruebas

Para validar el funcionamiento del reconocedor sobre los casos de prueba incluidos:

```bash
python test_cases.py
```

---

## Estructura del Repositorio

- Dockerfile: Definicion de la imagen base con Python 3.12 y descarga de modelos spaCy (es_core_news_sm y en_core_web_sm).
- docker-compose.yml: Archivo de orquestacion para iniciar el servicio en el puerto 8000.
- main.py: Servicio web en FastAPI que expone la interfaz y la API de procesamiento.
- enterprise_recognizers.py: Modulo con las expresiones regulares y patrones contextuales en espanol.
- test_cases.py: Suite de pruebas con casos contractuales y legales.
- requirements.txt: Lista de dependencias de Python.
- templates/index.html: Interfaz de usuario.
- .gitignore: Exclusiones de archivos temporales de Python y del sistema.

---

## Detener el Contenedor

Para detener la ejecucion del contenedor:
```bash
docker compose down
```
