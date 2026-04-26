"""
Módulo Auto-Ticketera: Jira Atlassian
=====================================
Implementa acciones correctivas y seguimientos trazables inyectando automáticamente
issues y tareas generadas por los agentes FinOps a un kanban o lista en Jira.
Se proveen bloqueos simples (JQL) para anular duplicaciones ridículas de la IA si el ticket aún está en Active.
"""

import os
from atlassian import Jira
from google.cloud import secretmanager

def get_secret_value(secret_id: str) -> str:
    """Extrae el secreto desde Google Secret Manager si se provee la ruta (projects/.../secrets/...)"""
    if not secret_id.startswith("projects/"):
        return secret_id
    try:
        client = secretmanager.SecretManagerServiceClient()
        response = client.access_secret_version(request={"name": secret_id})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"[!] Fallo al recuperar el secreto {secret_id}: {e}")
        return ""

def get_jira_client() -> Jira:
    """
    Arranca la sesión oficial con Atlassian. Valida tokens preferentemente montados 
    como volúmenes tipo 'Secret' para salvaguardar `JIRA_API_TOKEN`.
    """
    token_env = os.getenv("JIRA_API_TOKEN", "REPLACE_WITH_TOKEN_AT_GCP_SECRETMANAGER")
    actual_token = get_secret_value(token_env)
    
    return Jira(
        url=os.getenv("JIRA_URL", "https://pisa.atlassian.net/"),
        username=os.getenv("JIRA_USERNAME", "marmejia@corpcab.com.mx"),
        password=actual_token, 
        cloud=True
    )

def create_finops_ticket(
    finding_type: str,
    project_key: str,
    summary: str,
    description: str,
    priority: str = "Medium",
    labels: list = None,
    gcp_project: str = "",
) -> dict:
    """
    Función Tool del agente para instanciar Issue objects Jira. 
    Actúa con un filtro seguro (Safe Guard). Previo a accionar la bandera POST,
    consulta (vía JQL) si un ticket hermano sigue sin atenderse para sumar un
    comentario recriminatorio al mismo en lugar de ensuciar el board del Service Desk.
    """
    try:
        jira = get_jira_client()
        
        # Filtro condicional JQL: Limita si el issue con 'finops' parecido del projecto sigue vivo.
        jql = (
            f'project = "{project_key}" '
            f'AND summary ~ "{summary[:80]}" '
            f'AND status NOT IN (Done, Closed, Resolved) '
            f'AND labels = "finops"'
        )
        existing = jira.jql(jql, limit=1)
        
        # Si arroja hits de array => Hay duplicidad operativa. Comentar sobre el ticket sin generar sobrecarga.
        if existing.get("total", 0) > 0:
            existing_key = existing["issues"][0]["key"]
            jira.issue_add_comment(
                existing_key,
                f"⚡ [Actualización Automatizada] Hallazgo recurrente detectado de forma sistemática por el Agente Supervisor ADK (Clase: {finding_type}).\\n"
                f"Proyecto atado GCP: {gcp_project}\\n"
                f"La ventana de eficiencia requiere cerrar este hallazgo para liberar capital mensurable."
            )
            return {"action": "comment_added", "key": existing_key}

        # Tablas de correlación contextual => Severidades y tags
        issue_type_map = {
            "anomaly": "Bug",
            "rightsizing": "Task",
            "cud": "Story",
            "orphan": "Task",
            "bigquery": "Task",
            "cleanup": "Task",
        }

        # Payload serializado compatible Atlassian
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issue_type_map.get(finding_type, "Task")},
            "priority": {"name": priority},
            "labels": labels or ["finops", finding_type],
        }

        new_issue = jira.issue_create(fields=fields)
        return {"action": "created", "key": new_issue.get("key")}
    except Exception as e:
        print(f"[!] Caos transaccional: Excepción inyectando API hacia Jira Cloud en '{summary}': {e}")
        return {"action": "failed", "error": str(e)}
