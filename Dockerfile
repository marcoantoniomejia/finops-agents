# Use the official Python image
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True

WORKDIR /app

# Install production dependencies.
# NOTA: google-cloud-storage incluido en requirements.txt pero no estaba en el Dockerfile original
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
        "google-adk>=1.0.0" \
        "google-cloud-bigquery>=3.0.0" \
        "google-cloud-compute>=1.0.0" \
        "google-cloud-recommender>=2.0.0" \
        "google-cloud-monitoring>=2.0.0" \
        "google-cloud-storage>=2.0.0" \
        "google-cloud-secret-manager>=2.0.0" \
        "atlassian-python-api>=3.0.0" \
        "fastapi>=0.110.0" \
        "uvicorn[standard]>=0.29.0"

# Copy local code to the container image.
COPY src/ ./src/

# CORRECCIÓN: PYTHONPATH apunta a /app (no /app/src) para que los imports
# de la forma `from src.tools.billing import ...` funcionen correctamente.
ENV PYTHONPATH=/app

# Variables de entorno base — sobreescribibles en Cloud Run
ENV GOOGLE_CLOUD_LOCATION=us-central1
# Habilita Vertex AI como backend de ADK (en lugar de la Generative Language API pública)
ENV GOOGLE_GENAI_USE_VERTEXAI=TRUE

# CORRECCIÓN: El módulo de entrada es src.main:app (no main:app)
# ya que PYTHONPATH=/app y el archivo está en /app/src/main.py
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
