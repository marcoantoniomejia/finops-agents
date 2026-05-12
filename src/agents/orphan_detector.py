"""
Agente Buscador de Recursos Huérfanos
=====================================
Uno de los agentes medulares del v2.1. Examina la organización buscando aquellos
artefactos silenciosos que se quedan aprovisionados cobrando hora con hora sin tener un servicio anclado.
"""

from google.adk.agents import LlmAgent
from src.tools.compute_resources import find_orphaned_ips, find_unattached_disks
from src.tools.project_scanner import find_zero_billing_projects

# ==============================================================
# Definición formal del Agente ADK utilizando Gemini (Backend)
# ==============================================================
orphan_detector_agent = LlmAgent(
    name="orphan_detector",
    model="gemini-2.5-pro",
    output_key="orphan_detector_output",
    instruction=(
        "Eres un cazador de código y FinOps senior de PISA trabajando proactivamente para recuperar el dinero que se "
        "imprime al aire gracias a los 'recursos huérfanos' o desvinculados.\n"
        "Tu tarea vitalicia es escanear sin cesar la conectividad de la infraestructura para erradicar lo innecesario "
        "(Por ejemplo: IPs Estáticas pagadas sin asociar a ninguna máquina virtual u balanceador, discos Persistentes "
        "desconectados de cualquier instancia madre, y finalmente, cascarones vacíos: proyectos sin costo de facturación mensual).\n"
        "Compila todos estos crímenes financieros e impleméntalos en el informe tabular markdown con las siguientes cabezas de puente:\n"
        "[ID Proyecto GCP, Clase de Artefacto, Alias / Título, Ubicación Geográfica, Derroche Mensual Proyectado, Medida de Acción]."
        "Importante: Mantén un tono resolutivo y nunca ofrezcas borrar tajantemente cosas ajenas sin recomendar firmemente validarlo primero."
    ),
    tools=[
        find_orphaned_ips,
        find_unattached_disks,
        find_zero_billing_projects
    ]
)
