"""
Módulo de Integración con Google Cloud Monitoring (Métricas Crudas)
===================================================================
A menudo Recommender solo nos regala suposiciones. Monitoring (antiguamente Stackdriver)
nos brinda los vectores, las unidades tangibles numéricas necesarias. Usamos a Monitoring
para confirmar si el 15% de procesador nos conviene mantenerlo o no.
"""

from google.cloud import monitoring_v3
from typing import Optional
import os
import time

def get_vm_utilization(project_id: Optional[str] = None, instance_name: Optional[str] = None) -> float:
    """
    Obtiene la utilización real promediada de CPU de una VM en los últimos 14 días
    usando la API de Cloud Monitoring.

    Métrica: compute.googleapis.com/instance/cpu/utilization
    Si no se especifica instance_name, retorna el promedio global de todas las VMs del proyecto.
    Si la consulta falla (permisos, sin datos), retorna -1.0 como señal de dato no disponible.
    """
    project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT", "psa-infra-app-mx-dev-proj")
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{project_id}"

    # Ventana de los últimos 14 días en segundos
    now = time.time()
    seconds_14_days = 14 * 24 * 60 * 60
    interval = monitoring_v3.TimeInterval(
        {
            "end_time": {"seconds": int(now)},
            "start_time": {"seconds": int(now - seconds_14_days)},
        }
    )

    # Filtro base por métrica
    metric_filter = 'metric.type="compute.googleapis.com/instance/cpu/utilization"'
    if instance_name:
        metric_filter += f' AND metric.labels.instance_name="{instance_name}"'

    aggregation = monitoring_v3.Aggregation(
        {
            "alignment_period": {"seconds": seconds_14_days},  # Agregación en toda la ventana
            "per_series_aligner": monitoring_v3.Aggregation.Aligner.ALIGN_MEAN,
            "cross_series_reducer": monitoring_v3.Aggregation.Reducer.REDUCE_MEAN,
            "group_by_fields": [],
        }
    )

    try:
        results = client.list_time_series(
            request={
                "name": project_name,
                "filter": metric_filter,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
                "aggregation": aggregation,
            }
        )

        # Extraer el valor del único punto agregado
        for series in results:
            if series.points:
                # El valor viene en porcentaje de 0 a 1 — convertimos a % legible
                utilization_pct = series.points[0].value.double_value * 100
                return round(utilization_pct, 2)

        return -1.0  # Sin datos disponibles para este proyecto/VM

    except Exception as e:
        print(f"[!] Error consultando Cloud Monitoring para {project_id}/{instance_name}: {e}")
        return -1.0


def calculate_savings(current_cost: float, recommended_cost: float) -> float:
    """
    Matemática simple por delegación de herramienta al agente de texto.
    Evita alucinaciones numéricas delegando restas de flotantes directos a código de Python.
    """
    return round(current_cost - recommended_cost, 2)
