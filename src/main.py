
from fastapi import FastAPI
import os
from src.orchestrator import execute_daily_finops_cycle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment setup
project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
location = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1') # Default if not set

if not project_id:
    logger.warning("GOOGLE_CLOUD_PROJECT environment variable is not set.")

app = FastAPI(
    title="PISA FinOps Agents Runner",
    description="API to trigger FinOps agent execution and report generation.",
    version="2.1.12" # Forced refresh 2.1.12
)

@app.post("/run-agents")
def run_agents_endpoint():
    """
    Triggers the FinOps agents execution via the Orchestrator.
    """
    logger.info("POST /run-agents endpoint called.")
    try:
        logger.info("Attempting to run agents...")
        # Execute the agents cycle
        execute_daily_finops_cycle()
        logger.info("Agents executed successfully.")
        return {"status": "success", "message": "Reporte generado y guardado en GCS.", "version": "2.1.12"}

    except Exception as e:
        logger.error(f"Error during agent execution: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

from fastapi.responses import HTMLResponse
from src.tools.storage import get_latest_report_from_gcs
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
            body {{ box-sizing: border-box; min-width: 200px; max-width: 980px; margin: 0 auto; padding: 45px; }}
            .markdown-body {{ padding: 45px; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        </style>
    </head>
    <body class="markdown-body">
        <div id="content">Cargando reporte...</div>
        <script>
            try {{
                const b64 = "{md_b64}";
                const md = atob(b64);
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

@app.get("/")
def health_check():
    """
    Health check endpoint.
    """
    logger.info("GET / health check endpoint called.")
    return {"status": "healthy", "message": "PISA FinOps Agents Runner API is running!"}

# Local execution setup (optional, but good practice)
if __name__ == "__main__":
    import uvicorn
    # Cloud Run injects the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Running local server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
