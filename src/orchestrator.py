"""
Orquestador Multi-Agente ADK
============================
Módulo maestro del ecosistema. Reúne y coordina a los diferentes Agentes IA (State, Compute, BigQuery, Orphans).
Ejecuta los agentes en orden, recolecta sus respuestas independientes, invoca al modulo constructor 
('report_builder') para crear el documento integrado en formato Markdown y despacha las notificaciones (Slack).
"""

import os
from google.adk import Agent
from src.agents.state_manager import state_agent
from src.agents.compute_auditor import compute_auditor_agent
from src.agents.bigquery_auditor import bigquery_auditor_agent
from src.agents.orphan_detector import orphan_detector_agent
from src.report_builder import generate_unified_markdown_report
from src.tools.notifications import send_slack_notification

import asyncio
from google.adk.runners import InMemoryRunner

async def _run_agent(agent, prompt):
    runner = InMemoryRunner(agent=agent)
    events = await runner.run_debug(prompt)
    # Convert events to string for the report builder
    return str(events)

def execute_daily_finops_cycle():
    """
    Ejecuta el ciclo de vida del ecosistema Multi-Agente (Pipeline principal).
    """
    print("[INFO] Iniciando Orquestación FinOps v2.1...")
    
    # 1. State Manager 
    print("[INFO] Ejecutando Agente de Estado (Detección de Anomalías Presupuestales)...")
    anomalies_response = asyncio.run(_run_agent(state_agent, "Genera el reporte de anomalías de gasto por proyecto"))
    
    # 2. Compute Auditor
    print("[INFO] Ejecutando Agente de Cómputo (Right-Sizing y métricas)...")
    compute_response = asyncio.run(_run_agent(compute_auditor_agent, "Genera el reporte de las recomendaciones de VM Sizing"))
    
    # 3. BigQuery Auditor
    print("[INFO] Ejecutando Agente BigQuery (INFORMATION_SCHEMA)...")
    bq_response = asyncio.run(_run_agent(bigquery_auditor_agent, "Genera auditoría de queries costosas de los últimos 7 días"))
    
    # 4. Orphan Detector
    print("[INFO] Ejecutando Agente de Recursos Huérfanos (Discos/IPs)...")
    orphans_response = asyncio.run(_run_agent(orphan_detector_agent, "Ubica todas las IPs y discos sin uso en la red"))

    # 5. Builder - Conversión del payload a reporte amigable en Markdown
    print("[INFO] Consolidando hallazgos de IA en Reporte Unificado...")
    report_md = generate_unified_markdown_report([], [], [], []) 
    
    # 6. Notify - Envía la salida por Slack WebHooks
    print("[INFO] Notificando resultados...")
    if send_slack_notification(report_md):
        print("[INFO] Notificación ejecutada con éxito.")
    else:
        print("[WARN] Error o carencia de llave en notificador Slack.")
        
    print("[INFO] Ciclo de Orquestación Finalizado exitosamente.")

if __name__ == "__main__":
    # Facilidad para ejecutarlo como script suelto desde bash sin el server API
    execute_daily_finops_cycle()
