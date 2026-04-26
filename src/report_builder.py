"""
Taller Creador de Reportes (Report Builder)
===========================================
Consolida los reportes generados por cada agente en un documento único.
"""

from datetime import datetime

def generate_unified_markdown_report(anomalies_txt: str, compute_txt: str, bq_txt: str, orphans_txt: str) -> str:
    """
    Consolida las respuestas de texto de los diversos sub-agentes 
    en un solo documento visual unificado.
    
    Args:
        anomalies_txt (str): Markdown del State Manager.
        compute_txt (str): Markdown del Compute Auditor.
        bq_txt (str): Markdown del BQ Auditor.
        orphans_txt (str): Markdown del Orphan Detector.
        
    Returns:
        str: Reporte final consolidado.
    """
    
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    report = f"# 📊 Reporte Maestro FinOps PiSA — {today}\\n\\n"
    report += "Este reporte ha sido generado de manera autónoma por el clúster de agentes de IA.\\n\\n"
    
    report += "## 📈 1. Análisis de Facturación y Anomalías\\n"
    report += f"{anomalies_txt}\\n\\n"
    
    report += "## 🖥️ 2. Recomendaciones de Cómputo (Right-sizing)\\n"
    report += f"{compute_txt}\\n\\n"
    
    report += "## 📊 3. Auditoría de BigQuery (Eficiencia de Datos)\\n"
    report += f"{bq_txt}\\n\\n"
    
    report += "## 🗑️ 4. Recursos Huérfanos y Limpieza\\n"
    report += f"{orphans_txt}\\n\\n"
    
    report += "---\\n"
    report += "_Generado por FinOps Agents v2.1 (Vertex AI)_\\n"
    
    return report
