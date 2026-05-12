"""
Agente Auditor de Procesamiento de Bases de Datos (BigQuery)
============================================================
Agente IA centrado en analizar a detalle los esquemas generados por BigQuery y
su facturación sobre demanda (On-Demand). Es el encargado de identificar consultas
muy devoradoras o ineficientemente lanzadas por usuarios.
"""

from google.adk.agents import LlmAgent
from src.tools.bigquery_audit import get_expensive_queries, get_unpartitioned_tables, get_slot_utilization

# ==============================================================
# Definición formal del Agente ADK utilizando Gemini (Backend)
# ==============================================================
bigquery_auditor_agent = LlmAgent(
    name="bigquery_auditor",
    model="gemini-2.5-pro",
    output_key="bigquery_auditor_output",
    instruction=(
        "Eres un Agente FinOps altamente técnico y de carácter fiscalizador en ecosistemas de Datos de Google (BigQuery).\n"
        "Analiza las sentencias o consultas ineficientes catalogadas como 'expensive queries'. Considera también revisar "
        "la estructura general tabular descubriendo falta de esquemas sensatos o nulo particionamiento en volumen >1GB.\n"
        "Usa por convención matemática el 'On-demand pricing standard' de Google ($6.25 USD teóricos por cada 1 TB procesado) "
        "para inferir y calcular rudimentariamente el costo de cada query listada.\n"
        "La salida estándar al delegador padre debe ser obligatoriamente una tabla markdown con la firma semántica: "
        "[Proyecto de Datos, Hash del JOB ID, Email de Usuario, Terabytes Procesados, Fuga Calculada en $, Sugerencia de Partición]."
    ),
    tools=[
        get_expensive_queries,
        get_unpartitioned_tables,
        get_slot_utilization
    ]
)
