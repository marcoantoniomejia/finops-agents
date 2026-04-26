"""
Herramienta de Almacenamiento (Storage Tool)
===========================================
Gestiona la persistencia de los reportes generados en Google Cloud Storage.
"""

import os
from google.cloud import storage
from datetime import datetime

BUCKET_NAME = os.environ.get("REPORTS_BUCKET", "psa-finops-reports-1075963420777")

def save_report_to_gcs(report_content: str):
    """
    Sube el contenido del reporte a un bucket de GCS.
    Guarda una copia histórica con timestamp y sobreescribe el archivo 'latest.md'.
    """
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    
    # Nombre de archivo con fecha para histórico
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_history = bucket.blob(f"reports/report_{timestamp}.md")
    blob_history.upload_from_string(report_content, content_type="text/markdown")
    
    # Actualizar el puntero al último reporte
    blob_latest = bucket.blob("latest.md")
    blob_latest.upload_from_string(report_content, content_type="text/markdown")
    
    print(f"[STORAGE] Reporte guardado en gs://{BUCKET_NAME}/latest.md")

def save_agent_raw_data(agent_name: str, content: str):
    """
    Guarda la respuesta individual de un agente para depuración o auditoría detallada.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"raw_data/{agent_name}_latest.md")
        blob.upload_from_string(content, content_type="text/markdown")
        print(f"[STORAGE] Datos crudos de {agent_name} guardados en GCS.")
    except Exception as e:
        print(f"[ERROR STORAGE] No se pudo guardar raw data de {agent_name}: {e}")

def get_latest_report_from_gcs() -> str:
    """
    Recupera el contenido del último reporte generado.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob("latest.md")
        return blob.download_as_text()
    except Exception as e:
        return f"# Error\\nNo se pudo recuperar el reporte: {str(e)}"
