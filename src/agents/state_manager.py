"""
Agente State Manager (Gestor de Estado y Anomalías)
===================================================
Este módulo define al Agente responsable de estudiar el estado macro financiero de
los proyectos dentro de GCP usando métricas extraídas directamente de la exportación de
Billing de Google en BigQuery.

Lógica general:
Compara el consumo del mes actual, sumando los costos menos créditos, para un `project_id`, 
contra su símil reportado el mes inmediato anterior, calculando el aumento porcentual.
"""

from google.adk import Agent
from src.tools.billing import get_current_month_spend_by_project, get_previous_month_spend_by_project, get_top_services_delta
from typing import List

class AnomalyAlert:
    """Clase Modelo (Data Transfer Object) para serializar las Alertas de incrementos."""
    def __init__(self, project: str, severity: str, delta: float, current: float, previous: float, top_services: list, reason: str = ""):
        self.project = project
        self.severity = severity  # "HIGH", "MEDIUM", "LOW"
        self.delta = delta        # Porcentaje de crecimiento Ej: 15.5
        self.current = current    # Dólares actuales 
        self.previous = previous  # Dólares mes pasado
        self.top_services = top_services # Contexto descriptivo (Ej: [Cloud Run, Compute Engine])
        self.reason = reason      # Observaciones

def detect_anomalies_per_project(threshold: float = 10.0) -> List[AnomalyAlert]:
    """
    Función Tool primaria. Detecta anomalías de gasto por cada proyecto GCP 
    comparando las extracciones del dataset de facturación.
    
    Args:
        threshold (float): Limite tolerado de crecimiento orgánico antes de lanzar alerta (default 10%).
    Returns:
        List[AnomalyAlert]: Arreglo de artefactos de alerta que las siguientes fases evalúan o notifican.
    """
    current_data = get_current_month_spend_by_project()
    previous_data = get_previous_month_spend_by_project()
    
    alerts = []
    
    # Análisis comparativo transaccional iterando proyectos reportados el mes actual
    for project_id, current_spend in current_data.items():
        previous_spend = previous_data.get(project_id, 0)
        
        if previous_spend == 0:
            if current_spend > 0:
                alerts.append(AnomalyAlert(
                    project=project_id, 
                    severity="MEDIUM",
                    reason="La plataforma detectó ingresos en un proyecto que el mes anterior estaba en $0.", 
                    delta=100.0,
                    current=current_spend,
                    previous=0.0,
                    top_services=[]
                ))
            continue
            
        # Delta = ((Final - Inicial) / Inicial) * 100
        delta_pct = ((current_spend - previous_spend) / previous_spend) * 100
        
        # Inserción de la Alerta en memoria de acuerdo al limitante definido (10%)
        if delta_pct > threshold:
            alerts.append(AnomalyAlert(
                project=project_id, 
                severity="HIGH" if delta_pct > 25 else "MEDIUM",
                delta=delta_pct, 
                current=current_spend, 
                previous=previous_spend,
                top_services=get_top_services_delta(project_id),
                reason=f"Gasto excedió drásticamente el threshold preconfigurado del {threshold}%"
            ))
            
    return alerts

# ==============================================================
# Definición formal del Agente ADK utilizando Gemini (Backend)
# ==============================================================
state_agent = Agent(
    name="state_agent",
    instruction=(
        "Eres un Agente FinOps de Nivel Ejecutivo especializado en detectar anomalías de facturación agresivas.\n"
        "Compara el gasto monetario acumulado del mes actual contra el mes anterior segmentando por proyecto GCP.\n"
        "Usa las herramientas (tools) de Python subyacentes para investigar y consolidar los reportes devueltos de diccionarios a tablas.\n"
        "Si generas una tabla, las cabeceras ideales son: Proyecto, Mes Actual, Mes Anterior, Porcentaje y Severidad."
    ),
    tools=[
        get_current_month_spend_by_project,
        get_previous_month_spend_by_project,
        detect_anomalies_per_project
    ]
)
