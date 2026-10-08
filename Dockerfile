FROM python:3.12-slim

# Evitar buffers y escribir directo en consola
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar paquetes Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar los modelos spaCy necesarios para Presidio (inglés y español)
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download es_core_news_sm

# Copiar el código de la aplicación y plantillas
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
