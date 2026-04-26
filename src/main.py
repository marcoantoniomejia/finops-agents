"""
Módulo Principal - API de Cloud Run
===================================
Expone el orquestador Multi-Agente FinOps a través de la web empleando FastAPI.
De esta manera, servicios serverless como Google Cloud Scheduler pueden llamar a
`POST /run-agents` de manera diaria mediante una petición HTTP (cron).
"""

from fastapi import FastAPI
import os
from src.orchestrator import execute_daily_finops_cycle

# Instanciación de la aplicación FastAPI
app = FastAPI(
    title="PISA FinOps Multi-Agent API",
    description="Portal HTTP Serverless para invocar la ejecución del clúster de agentes autónomos.",
    version="2.1"
)

@app.get("/")
def health_check():
    """Health check para Cloud Run y navegadores."""
    return {
        "status": "healthy",
        "service": "PISA FinOps Multi-Agent API",
        "version": "2.1",
        "endpoints": {
            "POST /run-agents": "Ejecuta el ciclo completo de análisis FinOps"
        }
    }

@app.post("/run-agents")
def run_agents():
    """
    Endpoint principal expuesto a Cloud Scheduler.
    Se ejecuta a intervalos de 24 horas. Inicia todo el ciclo de diagnóstico de FinOps
    (Estado, Cómputo, Datos, Huérfanos) y termina consolidando los resultados en Jira.
    
    Retorna un diccionario JSON confirmando la ejecución exitosa de los scripts.
    """
    execute_daily_finops_cycle()
    return {"status": "ok", "message": "FinOps daily run completed successfully."}

if __name__ == "__main__":
    import uvicorn
    # Lanzamiento para pruebas en el entorno de desarrollo local (Antigravity).
    # Obtiene el puerto dinámico necesario (usualmente manejado por la nube como 8080).
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
