"""
Herramientas Inteligentes para la Recommender API (Sizing y CUDs)
=================================================================
Módulo de Machine Learning indirecto. Llama a los modelos de GCP pre-entrenados para recabar
recomendaciones emitidas directamente por Google hacia nuestra infraestructura en materia de tamaño
de servidores (Instances) y descuentos por compromisos volumétricos (CUDs, uso garantizado 1-3 años).
"""

from google.cloud import recommender_v1
import os

def get_vm_sizing_recommendations(project_id: str = None, zone: str = "us-central1-a") -> list:
    """
    Tool FinOps. Acude al servicio Recommender API para recabar un análisis heurístico hecho por
    GCP sobre las VMs desplegadas que pueden ajustarse (subirse o bajarse).
    
    Normaliza el objeto RPC Recommender en un listado tabular útil para que el Prompter IA 
    infiera y determine si aplicar el cambio.
    """
    client = recommender_v1.RecommenderClient()
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "psa-infra-app-mx-dev-proj")
    parent = f"projects/{project_id}/locations/{zone}/recommenders/google.compute.instance.MachineTypeRecommender"
    
    recommendations = []
    try:
        # Paginación simplificada y listado de insights.
        for rec in client.list_recommendations(parent=parent):
            # Parseamos el ahorro en USD usando el type float de money standard en proto (units + nanos/1e9)
            cost_proj = getattr(rec.primary_impact, "cost_projection", None)
            savings = 0.0
            if cost_proj and hasattr(cost_proj, "cost"):
                 savings = cost_proj.cost.units + (cost_proj.cost.nanos / 1e9)
                 
            rec_data = {
                "project": project_id,
                "description": rec.description,
                "state": rec.state_info.state.name,
                "savings_usd_per_month": abs(savings),
            }
            recommendations.append(rec_data)
    except Exception as e:
        print(f"[!] Error extrayendo recomendaciones de GCP ({project_id}): {e}")
        
    return recommendations

def get_cud_recommendations(project_id: str = None, billing_account_id: str = None) -> list:
    """
    Tool FinOps experimental para sugerencias de CUDs (Committed Use Discounts).
    Actualmente el Agente la usará de base para referenciar ahorros.
    """
    # En producción este método solicitaría "SpendBasedCommitmentRecommender"
    return []
