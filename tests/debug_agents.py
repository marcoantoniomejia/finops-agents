
import asyncio
import os
import sys

# Añadir src al path para que los imports internos funcionen
sys.path.append(os.path.join(os.getcwd(), "src"))

from google.adk.runners import InMemoryRunner
from agents.state_manager import state_agent

async def debug():
    print("Testing state_agent locally...")
    # Asegurar que las variables de entorno estén presentes
    os.environ["GOOGLE_CLOUD_PROJECT"] = "psa-infra-app-mx-dev-proj"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    
    try:
        runner = InMemoryRunner(agent=state_agent)
        # Usamos run directamente para ver el error crudo si ocurre
        response = await runner.run("Hola, genera un reporte de prueba.")
        print("Response received:")
        print(response)
    except Exception as e:
        print(f"EXCEPTION CAUGHT: {str(e)}")

if __name__ == "__main__":
    asyncio.run(debug())
