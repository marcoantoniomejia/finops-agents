"""
Explorador Holístico de Proyectos Inactivos (Project Scanner)
=============================================================
Un recurso huérfano también puede ser un sistema entero subyacente olvidado.
Esta utilidad aborda el concepto de 'Zero-cost Projects', referidos a proyectos
donde han pasado más de 'N' días inactivos sin un solo dólar operado.
"""

from google.cloud import bigquery
import os

def find_zero_billing_projects(days: int = 90) -> list:
    """
    Indaga en la métrica histórica (Facturación de Organización) aquellos `project_id`
    que ya no han presentado métricas de cargo, permitiendo a los arquitectos apagarlos, 
    liberar cuotas y achicar la brecha de vulnerabilidades para Security.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "psa-infra-app-mx-dev-proj")
    client = bigquery.Client(project=project_id)
    
    table_id = "pisa-proyecto-de-monitoreo.billing_PiSA_corpcabUSD.gcp_billing_export_v1_018D25_BD21E0_DFDB79"
    
    # Query de compresión. Toma todas las fechas pasadas mayores al parámetro days (90 por defecto).
    query = f"""
    WITH project_spend AS (
      SELECT
        project.id AS project_id,
        project.name AS project_name,
        SUM(cost) AS total_cost
      FROM `{table_id}`
      WHERE usage_start_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
      GROUP BY project_id, project_name
    )
    SELECT
      project_id,
      project_name,
      total_cost,
      'APAGADO DE PROYECTO (SUJETO A AUTORIZACIÓN ARQUITECTURA)' AS accion_recomendada
    FROM project_spend
    WHERE total_cost = 0 OR total_cost IS NULL
    ORDER BY project_name
    """
    
    orphans = []
    try:
        results = client.query(query).result()
        for row in results:
            if row.project_id:
                orphans.append({
                    "project": row.project_id,
                    "type": "Proyecto GCP Zombie / Inactivo",
                    "name": row.project_name,
                    "region": "Global", # El proyecto como unidad estructural existe globalmente
                    "cost_estimate_usd": 0.0, # Sin impacto monetario pero con impacto de gobernanza o cuota.
                    "action": row.accion_recomendada
                })
    except Exception as e:
        print(f"[!] Falla escaneando tabla de Facturación con proyectos en cero {project_id}: {e}")
        
    return orphans
