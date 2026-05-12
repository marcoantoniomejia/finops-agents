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
from src.tools.storage import save_agent_raw_data, save_report_to_gcs

import asyncio
from google.adk.runners import InMemoryRunner

async def _run_agent(agent, prompt):
    try:
        runner = InMemoryRunner(agent=agent)
        events = await runner.run_debug(prompt)
        
        final_text = ""
        
        for event in events:
            # Buscamos texto de forma exhaustiva en el evento
            candidates = []
            
            if hasattr(event, "text") and event.text:
                candidates.append(str(event.text))
                
            if hasattr(event, "content") and event.content:
                content = event.content
                if hasattr(content, "text") and content.text:
                    candidates.append(str(content.text))
                elif isinstance(content, list):
                    for part in content:
                        if hasattr(part, "text") and part.text:
                            candidates.append(str(part.text))
                elif isinstance(content, str):
                    candidates.append(content)
            
            if hasattr(event, "call") and event.call and hasattr(event.call, "response"):
                 resp = event.call.response
                 if hasattr(resp, "text") and resp.text:
                     candidates.append(str(resp.text))

            if candidates:
                valid_candidates = [c for c in candidates if len(c) > 10]
                if valid_candidates:
                    final_text = valid_candidates[-1]
                else:
                    final_text = candidates[-1]

        if not final_text:
            return f"El agente {agent.name} no pudo redactar su informe (Eventos: {len(events)})."
            
        return final_text
    except Exception as e:
        return f"⚠️ Error en el agente {agent.name}: {str(e)}"

def execute_daily_finops_cycle():
    """
    Ejecuta el ciclo de vida del ecosistema Multi-Agente (Pipeline principal).
    """
    print(f"[DEBUG] PROJECT_ID: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"[DEBUG] LOCATION: {os.environ.get('GOOGLE_CLOUD_LOCATION')}")
    print("[INFO] Iniciando Orquestación FinOps v2.1.12 (FORCE REFRESH GEMINI 3.1)...")
    
    # 1. State Manager 
    print("[INFO] Ejecutando Agente de Estado (Detección de Anomalías Presupuestales)...")
    anomalies_response = asyncio.run(_run_agent(state_agent, "Genera el reporte de anomalías de gasto por proyecto"))
    save_agent_raw_data("state_manager", anomalies_response)
    
    # 2. Compute Auditor
    print("[INFO] Ejecutando Agente de Cómputo (Right-Sizing y métricas)...")
    compute_response = asyncio.run(_run_agent(compute_auditor_agent, "Genera el reporte de las recomendaciones de VM Sizing"))
    save_agent_raw_data("compute_auditor", compute_response)
    
    # 3. BigQuery Auditor
    print("[INFO] Ejecutando Agente BigQuery (INFORMATION_SCHEMA)...")
    bq_response = asyncio.run(_run_agent(bigquery_auditor_agent, "Genera auditoría de queries costosas de los últimos 7 días"))
    save_agent_raw_data("bigquery_auditor", bq_response)
    
    # 4. Orphan Detector
    print("[INFO] Ejecutando Agente de Recursos Huérfanos (Discos/IPs)...")
    orphans_response = asyncio.run(_run_agent(orphan_detector_agent, "Ubica todas las IPs y discos sin uso en la red"))
    save_agent_raw_data("orphan_detector", orphans_response)

    # 5. Builder - Conversión del payload a reporte amigable en Markdown
    print("[INFO] Consolidando hallazgos de IA en Reporte Unificado...")
    report_md = generate_unified_markdown_report(
        anomalies_response, 
        compute_response, 
        bq_response, 
        orphans_response
    ) 
    
    # 6. Storage - Persiste el reporte en GCS para visualización web
    print("[INFO] Guardando reporte en Cloud Storage...")
    save_report_to_gcs(report_md)
    
    # 7. Notify - Envía la salida por Slack WebHooks
    print("[INFO] Notificando resultados...")
    if send_slack_notification(report_md):
        print("[INFO] Notificación ejecutada con éxito.")
    else:
        print("[WARN] Error o carencia de llave en notificador Slack.")
        
    print("[INFO] Ciclo de Orquestación Finalizado exitosamente.")

if __name__ == "__main__":
    # Facilidad para ejecutarlo como script suelto desde bash sin el server API
    execute_daily_finops_cycle()
