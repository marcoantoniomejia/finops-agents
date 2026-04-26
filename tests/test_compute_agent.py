import pytest
from unittest.mock import patch
from src.tools.recommender import get_vm_sizing_recommendations
from src.agents.compute_auditor import compute_auditor_agent

@patch('src.tools.recommender.recommender_v1.RecommenderClient')
def test_vm_recommendations(mock_client):
    # Mocking basic recommendator result
    mock_instance = mock_client.return_value
    mock_instance.list_recommendations.return_value = []
    
    # Validar que no lanza excepciones con input vacío
    result = get_vm_sizing_recommendations(project_id="test-project", zone="us-central1-a")
    assert isinstance(result, list)
    assert len(result) == 0

def test_compute_agent_tools():
    # Validar que el agente se ha inicializado con herramientas correctas
    tools_names = [tool.__name__ for tool in compute_auditor_agent.tools]
    assert "get_vm_sizing_recommendations" in tools_names
    assert "get_vm_utilization" in tools_names
