"""
Taller Creador de Reportes (Report Builder)
===========================================
Formatea los objetos puros extraídos por las herramientas de backend 
en una representación amena y bien maquetada en lenguaje Markdown,
lista para renderizarse en Slack, GitHub, Correos electrónicos o Jira tickets.
"""

from datetime import datetime

def generate_unified_markdown_report(anomalies: list, compute_results: list, bq_results: list, orphans: list) -> str:
    """
    Consolida las respuestas de las auditorías de los diversos sub-agentes 
    en un solo documento visual unificado tipo Newsletter / Resumen.
    
    Args:
        anomalies (list): Resultados de State Manager.
        compute_results (list): Resultados de Compute Auditor.
        bq_results (list): Resultados de BQ Auditor.
        orphans (list): Resultados de Recursos Huérfanos.
        
    Returns:
        str: Cadena formateada e indentada en Markdown (MD).
    """
    
    # Extraer el día en curso para rotular eficientemente el cuerpo del correo/slack/log
    today = datetime.now().strftime("%Y-%m-%d")
    report = f"# 📊 Reporte FinOps Diario — {today}\\n"
    report += "## Organización Operativa: corpcab.com.mx\\n\\n"
    
    report += "### 🔴 Alertas Críticas (Insights Detectados de Alto Nivel)\\n"
    
    # Desglose de Alertas y Severidades tempranas
    if not anomalies and not orphans:
         report += "- ✨ Todo está operando eficientemente. Sin anomalías severas detectadas en el clúster.\\n"
    
    for a in anomalies:
         # Asumimos una dataclass AnomalyAlert generada por state_manager
         report += f"- 🔴 [ANOMALÍA] Proyecto `{a.project}`: aumento severo del {a.delta:.1f}% en gasto general.\\n"
    
    for o in orphans:
         # Recursos que no devuelven nada pero gastan horas-USD
         report += f"- 🗑️ [HUÉRFANO] {o.get('type')} `{o.get('name')}` detectado en `{o.get('project')}`.\\n"
    
    # Secciones para que los managers profundicen
    report += "\\n### 📈 Sección 1: Desglose Mensual por Anomalías de Gasto\\n"
    report += "> _Agente: StateManager_ \\n\\n"
    # Pendiente iterar los objetos para crear tabla (project, score...)
    
    report += "\\n### 🖥️ Sección 2: Auditoría Integral de Cómputo (Right-sizing)\\n"
    report += "> _Agente: Compute Auditor_ \\n\\n"
    
    report += "\\n### 📊 Sección 3: Consulta Detallada a BigQuery\\n"
    report += "> _Agente: BigQuery Auditor_ \\n\\n"
    
    report += "\\n### 🗑️ Sección 4: Localización de Recursos Huérfanos\\n"
    report += "> _Agente: Orphan Detector_ \\n\\n"
    
    report += "\\n### 💰 Resumen Financiero de Ahorro Potencial\\n"
    report += "> _Estimaciones usando On-Demand Prices, sujetas a cambios regionales de GCP._ \\n\\n"
    
    return report
