# Presidio Shield - Anonimizador de Documentación Corporativa

Herramienta lista para producción y contenedorizada con **Docker**, diseñada para identificar y anonimizar datos personales sensibles (**PII**) en documentación empresarial, contratos y escrituras (adaptada especialmente al español e hispanoamérica).

---

## 🚀 Requisitos Previos

Solo necesitas tener instalado:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (o el motor de Docker en Linux/Mac).

---

## ⚡ Inicio Rápido (1 solo comando)

1. Abre tu terminal o consola en esta carpeta:
   ```bash
   cd presidio-app
   ```

2. Construye y levanta el contenedor:
   ```bash
   docker compose up --build
   ```

3. Abre tu navegador web en:
   👉 **http://localhost:8000**

¡Listo! Ya puedes pegar contratos o minutas legales para anonimizarlos.

---

## 🏷️ Entidades Reconocidas y Anonimizadas

El sistema cuenta con un motor enriquecido para español con reconocimiento de:

- **`<CL_RUT>`**: RUT chileno (con/sin puntos, guión y dígito verificador numérico o `K`).
- **`<ID_DOCUMENT>`**: Cédulas de identidad, DNIs y Pasaportes.
- **`<PERSON>`**: Nombres y apellidos completos vía NLP en español.
- **`<LOCATION>`**: Domicilios particulares y comerciales (pasajes, calles, avenidas, números, departamentos, oficinas, comunas y regiones).
- **`<PROFESSION>`**: Profesiones, oficios y cargos ejecutivos (abogado, ingeniero, gerente general, representante legal, etc.).
- **`<AGE>`**: Edad en lenguaje natural (*"de 21 años"*, *"tiene 30 años"*, *"edad: 45"*).
- **`<MARITAL_STATUS>`**: Estado civil (*soltero, casada, conviviente civil, etc.*).
- **`<IBAN_CODE>`**: Cuentas corrientes, vistas y cuentas bancarias.
- **`<FINANCIAL_AMOUNT>`**: Remuneraciones, montos de honorarios y pagos en CLP, UF, USD.
- **`<PHONE_NUMBER>`**: Teléfonos fijos y celulares chilenos/internacionales (`+56 9 ...`).
- **`<EMAIL_ADDRESS>`**: Correos electrónicos corporativos y personales.

---

## 🧪 Pruebas Automatizadas

Si deseas ejecutar la suite de casos de prueba incluidos:
```bash
python test_cases.py
```

---

## 📁 Estructura del Proyecto

```text
presidio-app/
├── Dockerfile                  # Configuración de la imagen y modelos spaCy
├── docker-compose.yml          # Orquestador del servicio en puerto 8000
├── requirements.txt            # Dependencias Python
├── main.py                     # API con FastAPI y orquestador de Presidio
├── enterprise_recognizers.py   # Reglas y patrones regex corporativos en español
├── test_cases.py               # Casos de prueba de validación
├── templates/
│   └── index.html              # Frontend web interactivo con UI moderna
└── README.md                   # Esta guía
```

---

## 🛑 Detener el Servicio

Para detener el contenedor en segundo plano:
```bash
docker compose down
```
