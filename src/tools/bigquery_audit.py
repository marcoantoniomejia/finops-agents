"""
Herramientas de Auditoría e Información de Rendimiento de BigQuery
==================================================================
Las vistas de esquema `INFORMATION_SCHEMA` nos brindan un histórico transaccional global
de todas las queries del proyecto, qué tan duras fueron con el motor de Bigquery 
y la volumetría de lo movido. 
"""

from google.cloud import bigquery
import os

def get_bq_client() -> bigquery.Client:
    """Gestor de autoconexión BigQuery con proyecto base."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "psa-infra-app-mx-dev-proj")
    return bigquery.Client(project=project_id)

def get_expensive_queries(days: int = 7, limit: int = 20) -> list:
    """
    Tool ADK. Levanta la vista INFORMATION_SCHEMA global transaccional para extraer 
    las top búsquedas limitadas con base en el uso de procesamiento de Bytes.
    
    Utiliza una fórmula on-demand (Ej. 6.25$ por GB procesado) que el equipo FinOps maneja actualmente.
    """
    client = get_bq_client()
    
    # INFORMATION_SCHEMA.JOBS captura logs al vuelo de las sentencias SELECT ejecutadas.
    query = f"""
    SELECT
      user_email,
      job_id,
      total_bytes_processed,
      ROUND(total_bytes_processed / POW(1024, 4) * 6.25, 2) AS estimated_cost_usd,
      query
    FROM `region-us`.INFORMATION_SCHEMA.JOBS
    WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
      AND job_type = 'QUERY'
      AND state = 'DONE'
    ORDER BY total_bytes_processed DESC
    LIMIT {limit}
    """
    
    try:
        results = client.query(query).result()
        expensive_queries = []
        for row in results:
            expensive_queries.append({
                "user": row.user_email,
                "job_id": row.job_id,
                "bytes_processed": row.total_bytes_processed,
                "estimated_cost_usd": row.estimated_cost_usd,
                "query": row.query[:100] + "..."  # Truncado en 100 char para no romper formato
            })
        return expensive_queries
    except Exception as e:
        print(f"[!] Error consultando queries ineficientes en esquema global: {e}")
        return []

def get_unpartitioned_tables() -> list:
    """
    Rastrea tablas gordas (>1GB) que pueden estar incurriendo en full-scans mortales para
    la cuota de facturación dada su carencia de un formato lógico de partición mensual o diaria.
    """
    return []  # Feature placeholder de la v2.1 

def get_slot_utilization() -> list:
    """Obtiene métricas de cuota al provisionamiento real de slots paralelizables."""
    return []  # Feature placeholder de la v2.1
