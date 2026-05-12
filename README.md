# FinOps Multi-Agent Ecosystem Assembled (GCP) 🤖📈

Este repositorio es la implementación en producción (v2.1) del Ecosistema Multi-Agente FinOps diseñado por el CoE de Cloud & AI Ops en PISA (`corpcab.com.mx`).

Este MVP (Minimum Viable Product) funciona bajo el **Google Agent Development Kit (ADK)**. Utiliza múltiples agentes de Inteligencia Artificial para auditar la infraestructura, bases de datos y finanzas de los proyectos de Google Cloud buscando eficiencia técnica y financiera (Right Sizing, Detección de Anomalías, Detección de elementos Huérfanos).

## Componentes y Arquitectura

El flujo de este sistema orquestador consta de 4 Sub-Agentes Inteligentes que operan en pipeline:

1. **State Manager (Gestor de Estado)**: Compara el gasto mes contra mes usando BigQuery Export. Identifica incrementos irregulares > 10%.
2. **Compute Auditor (Auditor Computacional)**: Evalúa las métricas de uso de CPU de las VMS para aprobar/denegar recomendaciones de la Recommender API.
3. **BigQuery Auditor (Auditor de Datos)**: Analiza el `INFORMATION_SCHEMA` para detectar consultas costosas y no optimizadas en las tablas.
4. **Orphan Detector (Buscador Huérfanos)**: Escanea la red de GCP en busca de Discos Persistentes desligados (unattached) y Direcciones IP externas facturando en vacío.

## Tecnologías Implementadas

- **Python 3.12**
- **Google Agent Development Kit (ADK)**
- **Cloud Run / FastAPI** (Orquestador cron-triggered)
- **BigQuery** (Histórico y Billing Export)
- **Atlassian Jira API** (Resolución automatizada a soporte IT)

## Instalación y Arranque Local

Para correr y depurar localmente:

```bash
pip install -r requirements.txt
# Requiere credenciales Default Auth de GCP
gcloud auth application-default login
# Servir en puerto local 8080
uvicorn src.main:app --reload
```

## Creación de Casos en Jira

El orquestador levanta issues en Jira ante cada evento. El token es necesario para crear los reportes:
`export JIRA_API_TOKEN="tu-token-atlassian"`
