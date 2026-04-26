"""
Módulo Principal - API de Cloud Run
===================================
Expone el orquestador Multi-Agente FinOps a través de la web empleando FastAPI.
De esta manera, servicios serverless como Google Cloud Scheduler pueden llamar a
`POST /run-agents` de manera diaria mediante una petición HTTP (cron).
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
from src.orchestrator import execute_daily_finops_cycle
from src.tools.storage import get_latest_report_from_gcs

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
            "POST /run-agents": "Ejecuta el ciclo completo de análisis FinOps",
            "GET /latest-report": "Visualiza el reporte más reciente en formato HTML"
        }
    }

import base64

@app.get("/latest-report", response_class=HTMLResponse)
def view_report():
    """
    Renderiza el contenido Markdown del último reporte como HTML 
    empleando un visor minimalista en el cliente (Marked.js).
    """
    md_content = get_latest_report_from_gcs()
    # Codificar en base64 para evitar problemas con comillas y backticks en el template JS
    md_b64 = base64.b64encode(md_content.encode('utf-8')).decode('utf-8')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reporte FinOps PiSA</title>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.css">
        <style>
            body {{
                box-sizing: border-box;
                min-width: 200px;
                max-width: 980px;
                margin: 0 auto;
                padding: 45px;
            }}
            .markdown-body {{
                padding: 45px;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            @media (max-width: 767px) {{
                .markdown-body {{
                    padding: 15px;
                }}
            }}
        </style>
    </head>
    <body class="markdown-body">
        <div id="content">Cargando reporte...</div>
        <script>
            try {{
                const b64 = "{md_b64}";
                const md = atob(b64);
                // Decodificar UTF-8 correctamente después de atob
                const decodeUtf8 = (s) => decodeURIComponent(escape(s));
                document.getElementById('content').innerHTML = marked.parse(decodeUtf8(md));
            }} catch (e) {{
                document.getElementById('content').innerHTML = "<h1>Error al cargar el reporte</h1><p>" + e.message + "</p>";
            }}
        </script>
    </body>
    </html>
    """
    return html_content

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
