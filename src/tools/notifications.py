"""
Canalizador de Notificaciones Slack/Email
=========================================
Controlador ligero para despachar las matrices documentales en markdown compiladas 
por el Orchestrator hacia Webhooks empresariales corporativos de Slack u O365/Email.
"""

import os
import urllib.request
import json

def send_slack_notification(message: str, webhook_url: str = None) -> bool:
    """
    Emite un POST JSON puro hacia un Incoming Webhook genérico de Slack.
    
    Args:
        message(str): Cuerpo ya sanitizado y curado por Report Builder del Agente.
        webhook_url(str): URL confidencial provista por Cloud Run Envs / Secret Manager.
    """
    webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("[WARN] Variable de entorno 'SLACK_WEBHOOK_URL' en silencio (vacía), no habrá emisión a Slack.")
        return False
        
    data = {"text": message}
    req = urllib.request.Request(
        webhook_url, 
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        # Llamada asíncrona síncrona simple
        urllib.request.urlopen(req)
        return True
    except Exception as e:
        print(f"[!] Frustración invocando canal Slack API: {e}")
        return False

def send_email_notification(subject: str, body: str, destination: str) -> bool:
    """Prototipo MVP v2.1. Puede interconectarse con módulos estandar de PISA O365 SMPT."""
    return True
