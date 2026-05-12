"""
Agente Auditor de Instancias Compute Engine
===========================================
Sub-Agente inteligente enfocado estrictamente a las Máquinas Virtuales (GCE).

Su objetivo es solicitar consejos nativos a la Recommender API y validarlos contra la
métrica activa de la VM. De existir una correlación (Por ej: Recomiendan bajar el
procesador y actualmente el consumo de CPU es del 10%), el Agente empuja esta
recomendación como válida para bajar la factura de Cómputo mensualmente ("Right-Sizing").
"""

from google.adk.agents import LlmAgent
from src.tools.recommender import get_vm_sizing_recommendations, get_cud_recommendations
from src.tools.monitoring import get_vm_utilization, calculate_savings

# ==============================================================
# Definición formal del Agente ADK utilizando Gemini (Backend)
# ==============================================================
compute_auditor_agent = LlmAgent(
    name="compute_auditor",
    model="gemini-2.5-pro",
    output_key="compute_auditor_output",
    instruction=(
        "Eres un Agente FinOps del CoE especializado en optimización de infraestructura (Cómputo/GCE) en Google Cloud.\n"
        "Estudia cuidadosamente las métricas de utilización de CPU que te devuelve la Tool y coteja con las "
        "recomendaciones directas del Recommender API de Google.\n"
        "Si la sugerencia es válida, apruébala y calcula los ahorros proyectados (Sizing/Right-Sizing).\n"
        "Toma en cuenta descuentos por uso comprometido (CUDs) cuando la capacidad utilizada sea plana y estable.\n"
        "Prioriza de forma crítica el despilfarro financiero por encima del optimizado micro.\n"
        "Al finalizar el reporte del modelo de lenguaje, expulsa SIEMPRE una tabla markdown con formato:\n"
        "[Proyecto, Nombre Máquina, Capacidad Actual, Orientación Recomendada, Proyección de Ahorro USD, Severidad]."
    ),
    tools=[
        get_vm_sizing_recommendations,
        get_cud_recommendations,
        get_vm_utilization,
        calculate_savings
    ]
)
