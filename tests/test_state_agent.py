import pytest
from unittest.mock import patch
from src.agents.state_manager import detect_anomalies_per_project

@patch('src.agents.state_manager.get_current_month_spend_by_project')
@patch('src.agents.state_manager.get_previous_month_spend_by_project')
def test_detect_anomalies(mock_previous, mock_current):
    # Setup mocks
    mock_current.return_value = {
        "psa-proyecto-normal": 100.0,
        "psa-proyecto-anomalia": 150.0,
        "psa-proyecto-nuevo": 50.0
    }
    
    mock_previous.return_value = {
        "psa-proyecto-normal": 95.0,  # +5%, no alert
        "psa-proyecto-anomalia": 100.0, # +50%, High severity alert
        # psa-proyecto-nuevo no existe en historico
    }
    
    alerts = detect_anomalies_per_project(threshold=10.0)
    
    assert len(alerts) == 2
    
    # Assert anomaly 1 (high severity)
    anomaly_alert = next((a for a in alerts if a.project == "psa-proyecto-anomalia"), None)
    assert anomaly_alert is not None
    assert anomaly_alert.severity == "HIGH"
    assert anomaly_alert.delta == 50.0
    
    # Assert new project (medium severity)
    new_project_alert = next((a for a in alerts if a.project == "psa-proyecto-nuevo"), None)
    assert new_project_alert is not None
    assert new_project_alert.severity == "MEDIUM"
    assert new_project_alert.delta == 100.0

