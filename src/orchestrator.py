"""
Orquestador Multi-Agente ADK
============================
Módulo maestro del ecosistema. Reúne y coordina a los diferentes Agentes IA (State, Compute, BigQuery, Orphans).
Ejecuta los agentes en orden, recolecta sus respuestas independientes, invoca al modulo constructor
('report_builder') para crear el documento integrado en formato Markdown y despacha las notificaciones (Slack).
"""

import os
import logging
from google.adk.agents import LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from src.agents.state_manager import state_agent
from src.agents.compute_auditor import compute_auditor_agent
from src.agents.bigquery_auditor import bigquery_auditor_agent
from src.agents.orphan_detector import orphan_detector_agent
from src.report_builder import generate_unified_markdown_report
from src.tools.notifications import send_slack_notification
from src.tools.storage import save_agent_raw_data, save_report_to_gcs

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# Helper: Ejecuta un agente ADK de forma asíncrona y extrae texto
# ---------------------------------------------------------------
async def _run_agent(agent: LlmAgent, prompt: str) -> str:
    """
    Ejecuta un agente ADK usando InMemoryRunner y retorna el texto de la respuesta final.
    Utiliza el output_key del agente para extraer la respuesta del estado de sesión cuando
    está disponible; de lo contrario, parsea los eventos del runner directamente.
    """
    try:
        session_service = InMemorySessionService()
        runner = InMemoryRunner(agent=agent, session_service=session_service)

        # Crear sesión y construir el mensaje de usuario
        session = await session_service.create_session(
            app_name=agent.name,
            user_id="finops-orchestrator"
        )
        user_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=prompt)]
        )

        final_text = ""

        # Iterar sobre los eventos que el runner emite (streaming ADK)
        async for event in runner.run_async(
            user_id="finops-orchestrator",
            session_id=session.id,
            new_message=user_message,
        ):
            # Extraer texto del evento de respuesta del modelo
            if (
                hasattr(event, "content")
                and event.content
                and hasattr(event.content, "parts")
            ):
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        final_text = part.text  # Tomamos la última parte de texto

        # Intentar recuperar resultado desde el output_key del estado de sesión
        if agent.output_key:
            refreshed = await session_service.get_session(
                app_name=agent.name,
                user_id="finops-orchestrator",
                session_id=session.id,
            )
            state_value = (refreshed.state or {}).get(agent.output_key, "")
            if state_value:
                final_text = str(state_value)

        if not final_text:
            return f"⚠️ El agente `{agent.name}` no produjo un informe legible."

        return final_text

    except Exception as e:
        logger.error(f"Error ejecutando agente {agent.name}: {e}", exc_info=True)
        return f"⚠️ Error en el agente `{agent.name}`: {str(e)}"


# ---------------------------------------------------------------
# Pipeline principal — debe llamarse desde un contexto async
# ---------------------------------------------------------------
async def execute_daily_finops_cycle():
    """
    Ejecuta el ciclo de vida del ecosistema Multi-Agente (Pipeline principal).
    Esta función es ASYNC para integrarse correctamente con FastAPI/uvicorn.
    """
    logger.info(f"[DEBUG] PROJECT_ID: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    logger.info(f"[DEBUG] LOCATION: {os.environ.get('GOOGLE_CLOUD_LOCATION')}")
    logger.info("[INFO] Iniciando Orquestación FinOps v2.2.0...")

    # 1. State Manager
    logger.info("[INFO] Ejecutando Agente de Estado (Detección de Anomalías Presupuestales)...")
    anomalies_response = await _run_agent(
        state_agent,
        "Genera el reporte de anomalías de gasto por proyecto"
    )
    save_agent_raw_data("state_manager", anomalies_response)

    # 2. Compute Auditor
    logger.info("[INFO] Ejecutando Agente de Cómputo (Right-Sizing y métricas)...")
    compute_response = await _run_agent(
        compute_auditor_agent,
        "Genera el reporte de las recomendaciones de VM Sizing"
    )
    save_agent_raw_data("compute_auditor", compute_response)

    # 3. BigQuery Auditor
    logger.info("[INFO] Ejecutando Agente BigQuery (INFORMATION_SCHEMA)...")
    bq_response = await _run_agent(
        bigquery_auditor_agent,
        "Genera auditoría de queries costosas de los últimos 7 días"
    )
    save_agent_raw_data("bigquery_auditor", bq_response)

    # 4. Orphan Detector
    logger.info("[INFO] Ejecutando Agente de Recursos Huérfanos (Discos/IPs)...")
    orphans_response = await _run_agent(
        orphan_detector_agent,
        "Ubica todas las IPs y discos sin uso en la red"
    )
    save_agent_raw_data("orphan_detector", orphans_response)

    # 5. Builder — Consolidación en reporte Markdown unificado
    logger.info("[INFO] Consolidando hallazgos de IA en Reporte Unificado...")
    report_md = generate_unified_markdown_report(
        anomalies_response,
        compute_response,
        bq_response,
        orphans_response
    )

    # 6. Storage — Persistencia en GCS
    logger.info("[INFO] Guardando reporte en Cloud Storage...")
    save_report_to_gcs(report_md)

    # 7. Notify — Slack WebHook
    logger.info("[INFO] Notificando resultados...")
    if send_slack_notification(report_md):
        logger.info("[INFO] Notificación ejecutada con éxito.")
    else:
        logger.warning("[WARN] Error o carencia de llave en notificador Slack.")

    logger.info("[INFO] Ciclo de Orquestación Finalizado exitosamente.")
    return report_md


if __name__ == "__main__":
    import asyncio
    # Permite ejecutarlo como script suelto desde bash sin el server API
    asyncio.run(execute_daily_finops_cycle())
