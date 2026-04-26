"""
Herramientas de Exportación de Billing (BigQuery)
=================================================
Módulo utilitario para establecer conectividad y realizar consultas SQL a la tabla
de exportación masiva nativa de facturación proporcionada por Google Cloud
a nivel de organización PISA (`billing_PiSA_corpcabUSD`).
"""

from google.cloud import bigquery
from typing import Dict, Any
import os

def get_bq_client() -> bigquery.Client:
    """
    Instancia del cliente BigQuery basándose en el proyecto de credenciales Default.
    """
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "psa-infra-app-mx-dev-proj")
    return bigquery.Client(project=project_id)

def get_current_month_spend_by_project() -> Dict[str, float]:
    """
    Función ADK Tool genérica. Suma a granularidad de proyecto toda la facturación bruta (cost) 
    incurrida durante el transcurso legal del mes actual (`invoice.month`).
    Sustrae de esta cuenta cualquier descuento de uso promocional (credits).
    
    Retorna:
    Un diccionario que mapea al formato { "hijo_proyecto_gcp": flotante_neto_usd }
    """
    client = get_bq_client()
    table_id = "pisa-proyecto-de-monitoreo.billing_PiSA_corpcabUSD.gcp_billing_export_v1_018D25_BD21E0_DFDB79"
    
    query = f"""
    SELECT
      project.id AS project_id,
      SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS costo_neto
    FROM `{table_id}`
    WHERE invoice.month = FORMAT_DATE('%Y%m', CURRENT_DATE())
    AND project.id IS NOT NULL
    GROUP BY project_id
    """
    
    # query_job maneja la canalización contra BQ mediante gRPC
    query_job = client.query(query)
    results = query_job.result()
    
    spend_data = {}
    for row in results:
        spend_data[row.project_id] = float(row.costo_neto)
        
    return spend_data

def get_previous_month_spend_by_project() -> Dict[str, float]:
    """
    Utilidad hermana de get_current_month_spend_by_project. 
    Se traslada a 1 mes exacto hacia atrás iterando los datos cristalizados facturados de allí.
    """
    client = get_bq_client()
    table_id = "pisa-proyecto-de-monitoreo.billing_PiSA_corpcabUSD.gcp_billing_export_v1_018D25_BD21E0_DFDB79"
    
    query = f"""
    SELECT
      project.id AS project_id,
      SUM(cost) + SUM(IFNULL((SELECT SUM(c.amount) FROM UNNEST(credits) c), 0)) AS costo_neto
    FROM `{table_id}`
    WHERE invoice.month = FORMAT_DATE('%Y%m', DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH))
    AND project.id IS NOT NULL
    GROUP BY project_id
    """
    
    query_job = client.query(query)
    results = query_job.result()
    
    spend_data = {}
    for row in results:
        spend_data[row.project_id] = float(row.costo_neto)
        
    return spend_data

def get_top_services_delta(project_id: str) -> list:
    """
    Placeholder: Eventualmente, al detectar incrementos bruscos, se mandaría llamar a
    una tercera query desglozada por columna `service.description` apuntando a dicho proyecto individual
    para reportarle a qué se le atribuye la culpa del incremento.
    """
    return ["Compute Engine", "Cloud Run"]
