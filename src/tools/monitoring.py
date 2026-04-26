"""
Módulo de Integración con Google Cloud Monitoring (Métricas Crudas)
===================================================================
A menudo Recommender solo nos regala suposiciones. Monitoring (antiguamente Stackdriver) 
nos brinda los vectores, las unidades tangibles numéricas necesarias. Usamos a Monitoring 
para confirmar si el 15% de procesador nos conviene mantenerlo o no.
"""

from google.cloud import monitoring_v3
from typing import Dict
import os
import time

def get_vm_utilization(project_id: str = None, instance_name: str = None) -> float:
    """
    Obtiene la utilización real agregada y promediada de la carga de procesadores (CPU)
    y en algunos OS configurados, el RAM. Evaluamos en periodos de 14 días.
    
    Nota Implementación MVP 2.1:
    Esto se encuentra en formato simulación para los testings hasta recibir permisos robustos 
    de visibilidad a la métrica: "compute.googleapis.com/instance/cpu/utilization"
    """
    return 15.5  # Retorna el uso promedio en coma flotante porcentual del 15.5% fijo

def calculate_savings(current_cost: float, recommended_cost: float) -> float:
    """
    Matemática simple por delegación de herramienta al agente de texto. 
    Evita alucinaciones numéricas delegando restas de flotantes directos a código de Python.
    """
    return current_cost - recommended_cost
