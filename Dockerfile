# Use the official Python image
FROM python:3.12-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

WORKDIR /app

# Install production dependencies.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir google-adk google-cloud-bigquery google-cloud-compute google-cloud-recommender google-cloud-monitoring google-cloud-secret-manager atlassian-python-api fastapi uvicorn

# Copy local code to the container image.
COPY src/ ./src/

# Run the web service on container startup
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
