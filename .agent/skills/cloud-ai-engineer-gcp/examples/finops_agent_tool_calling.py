import os
from google.cloud import bigquery
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, FunctionDeclaration

# Configuración inicial y mejores prácticas
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 1. Definición de Herramientas (Tools) para el Agente
# Permite al modelo ejecutar una consulta SQL para saber el gasto
def get_billing_data_schema():
    return FunctionDeclaration(
        name="query_monthly_billing",
        description="Obtiene el total gastado en GCP en el mes actual agrupado por servicio.",
        parameters={
            "type": "object",
            "properties": {
                "month": {"type": "string", "description": "Mes en formato YYYY-MM"}
            },
            "required": ["month"]
        }
    )

tools = Tool(function_declarations=[get_billing_data_schema()])

# 2. Instrucciones del Sistema para el Agente FinOps
system_instruction = (
    "Eres un Agente FinOps Experto en Google Cloud. Tu misión es analizar la "
    "facturación y proporcionar recomendaciones de optimización claras y accionables. "
    "Utiliza tus herramientas para consultar los costos reales cuando el usuario te lo pida. "
    "Muestra el impacto financiero de las recomendaciones."
)

# 3. Inicialización del Modelo Gemini
model = GenerativeModel(
    model_name="gemini-1.5-pro-preview-0409",
    tools=[tools],
    system_instruction=system_instruction
)

def analyze_finops_request(user_prompt: str) -> str:
    """Invoca al agente de FinOps para que analice la consulta."""
    chat = model.start_chat()
    response = chat.send_message(user_prompt)
    
    # Manejo de la llamada a la función (Tool calling)
    if response.candidates[0].function_calls:
        # Aquí se ejecutaría la lógica real contra BigQuery (simulado por brevedad)
        print("El agente decidió llamar a la herramienta:", response.candidates[0].function_calls[0].name)
        
        # Simulación de respuesta de BigQuery
        simulated_api_response = {"Compute Engine": "$1500", "Cloud SQL": "$450"}
        
        response = chat.send_message(
            [
                vertexai.generative_models.Part.from_function_response(
                    name="query_monthly_billing",
                    response={"content": simulated_api_response}
                )
            ]
        )
    return response.text

if __name__ == "__main__":
    prompt = "Dame un reporte de mis costos de este mes y recomiéndame si debo apagar algo."
    print("User:", prompt)
    print("Agent:\n", analyze_finops_request(prompt))
