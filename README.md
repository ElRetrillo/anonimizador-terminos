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

## Entidades Detectadas y Anonimizadas en Español

El motor cuenta con reconocedores entrenados y adaptados para terminología legal y contractual con etiquetas 100% en español y clasificación granular para evitar sobreutilizar categorías genéricas como Organización:

- `<RUT>`: Rol Único Tributario chileno con o sin puntos, guión y dígito verificador numérico o K (ej. `21.453.124-0`).
- `<PERSONA>`: Nombres y apellidos completos de personas naturales.
- `<EMPRESA>`: Razones sociales, sociedades por acciones (SpA), sociedades anónimas (S.A.), limitadas (Ltda.), EIRL, y corporaciones.
- `<ENTIDAD_BANCARIA>`: Bancos y entidades financieras (Banco Santander, Banco de Chile, BancoEstado, BCI, Scotiabank, Itaú, etc.).
- `<NOTARIA>`: Notarías públicas y notarios actuantes en escrituras y contratos.
- `<INSTITUCION_PUBLICA>`: Organismos del Estado y reguladores (SII, Tesorería General, Conservador de Bienes Raíces, Registro Civil, etc.).
- `<ORGANIZACION>`: Organizaciones civiles, gremiales y fundaciones.
- `<DIRECCION>`: Domicilios específicos, pasajes, calles, avenidas, departamentos y números de oficina.
- `<UBICACION>`: Ciudades, comunas, regiones y países.
- `<DOCUMENTO_IDENTIDAD>`: Cédulas de identidad, DNI y pasaportes.
- `<CARGO_O_PROFESION>`: Profesiones, oficios y cargos directivos (abogado, ingeniero, gerente general, representante legal, etc.).
- `<EDAD>`: Expresiones de edad en lenguaje natural (ej. "de 21 años", "edad: 40").
- `<ESTADO_CIVIL>`: Estado civil (soltero/a, casado/a, divorciado/a, viudo/a, conviviente civil).
- `<CUENTA_BANCARIA>`: Cuentas bancarias corrientes, vistas, RUT y cuentas de ahorro.
- `<MONTO_FINANCIERO>`: Montos, honorarios, remuneraciones y pagos en CLP, UF, USD o EUR.
- `<TELEFONO>`: Números telefónicos fijos y móviles.
- `<CORREO_ELECTRONICO>`: Direcciones de e-mail.
- `<NACIONALIDAD>`: Nacionalidad declarada en comparecencias.
- `<FECHA>`: Fechas contractuales en lenguaje formal o natural.

---

## Caracteristicas de la Interfaz Web

- **Modo Documento PDF**:
  - Subida mediante arrastrar y soltar (Drag & Drop) o explorador de archivos.
  - Escaneo automático de todas las páginas del PDF y detección de datos sensibles (PII).
  - Aplicación de redacciones criptográficas permanentes en las páginas del PDF.
  - Estilos de censura visual configurables (Etiqueta corporativa `[CL_RUT]`, Blackout sólido o Resalte protector).
  - Descarga inmediata del PDF anonimizado y del texto extraído (.txt).
  - **Gestión de almacenamiento libre de conflictos**: Los documentos se procesan en la carpeta local aislada `processed_docs/` con identificadores únicos UUID para prevenir sobreescrituras y colisiones.
  - **Política de privacidad estricta**: Opción predeterminada para eliminar el archivo del servidor de forma inmediata una vez finalizada la descarga (o vaciado manual mediante el botón de limpieza).
  - Limpieza automática de archivos temporales con más de 1 hora de antigüedad.
- **Modo Texto / Minuta**:
  - Procesamiento directo de minutas y fragmentos de texto en pantalla.
  - Plantillas de prueba integradas (Contrato Laboral, Poder Notarial, Pagos/Finanzas).
  - Botón de copiado directo al portapapeles.
- **Diseño y Estética**:
  - Diseño rectangular sobrio adaptado a estándares corporativos y legales.
  - Selector de modo oscuro y modo claro con persistencia de variables de diseño.
  - Métricas e insignias detalladas de entidades detectadas con nivel de confianza y número de página.

---

## Ejecucion de Pruebas

Para validar el funcionamiento del reconocedor sobre los casos de prueba incluidos:

```bash
python test_cases.py
```

---

## Estructura del Repositorio

- `Dockerfile`: Definición de la imagen base con Python 3.12, PyMuPDF y descarga de modelos spaCy (`es_core_news_sm` y `en_core_web_sm`).
- `docker-compose.yml`: Orquestación del servicio en el puerto 8000 con volumen montado para `processed_docs/`.
- `main.py`: Servicio FastAPI con endpoints para texto (`/api/anonymize`), escaneo/anonimización de PDF (`/api/anonymize-pdf`), descarga segura (`/api/download-pdf/{file_id}`) y vaciado (`/api/cleanup-docs`).
- `enterprise_recognizers.py`: Patrones regex y reconocedores contextuales para contratos en español (RUT, montos monetarios, cuentas bancarias, direcciones, etc.).
- `test_cases.py`: Suite de validación de casos empresariales.
- `requirements.txt`: Dependencias del sistema (FastAPI, PyMuPDF, python-multipart, Presidio, Jinja2).
- `processed_docs/`: Directorio dedicado al almacenamiento temporal y seguro de documentos procesados.
- `templates/index.html`: Interfaz corporativa con pestañas de modo PDF y texto libre.
- `.gitignore`: Exclusión de archivos procesados y temporales.

---

## Detener el Contenedor

Para detener la ejecucion del contenedor:
```bash
docker compose down
```
