
from report_builder import generate_unified_markdown_report

def test_report_formatting():
    # Simulamos respuestas de los agentes
    anomalies = "| Proyecto | Delta |\n|---|---|\n| PSA-DEV | 15% |"
    compute = "Recomendación: n2-standard-4 -> n2-standard-2"
    bq = "Query ID: abc123 - Costo: $5.0"
    orphans = "IP 1.2.3.4 sin uso"
    
    report = generate_unified_markdown_report(anomalies, compute, bq, orphans)
    
    print("--- Reporte Generado ---")
    print(report)
    print("------------------------")
    
    # Validaciones básicas
    assert "# 📊 Reporte Maestro FinOps PiSA" in report
    assert "## 📈 1. Análisis de Facturación y Anomalías" in report
    assert "PSA-DEV" in report
    assert "\n" in report # Verificar que hay saltos de línea reales
    print("\n✅ Validación de Report Builder: EXITOSA")

if __name__ == "__main__":
    test_report_formatting()
