from fastapi.testclient import TestClient
from main import app
from services.ml_service import ml_service

client = TestClient(app)

def test_production_ml_predict_endpoint():
    headers = {"Authorization": "Bearer mock_valid_token_prod_user_01"}

    # Distracted case
    payload_distracted = {
        "switch_frequency_5m": 12.0,
        "social_media_ratio": 0.50,
        "entertainment_ratio": 0.20,
        "idle_ratio": 0.05,
        "session_elapsed_minutes": 60.0,
        "time_of_day_hour": 15
    }

    res = client.post("/api/ml/predict", json=payload_distracted, headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Exact Schema Assertions
    assert "prediction" in data
    assert "probability" in data
    assert "model_version" in data
    assert "explanation_features" in data

    assert data["prediction"] in ["focused", "distracted"]
    assert 0.0 <= data["probability"] <= 1.0
    assert "v1.0.0" in data["model_version"]
    assert isinstance(data["explanation_features"], list)
    assert len(data["explanation_features"]) > 0

def test_production_ml_predict_focused_case():
    headers = {"Authorization": "Bearer mock_valid_token_prod_user_01"}

    payload_focused = {
        "switch_frequency_5m": 1.0,
        "social_media_ratio": 0.0,
        "entertainment_ratio": 0.0,
        "idle_ratio": 0.0,
        "session_elapsed_minutes": 15.0,
        "time_of_day_hour": 10
    }

    res = client.post("/api/ml/predict", json=payload_focused, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["prediction"] == "focused"
    assert data["probability"] < 0.5

def test_production_ml_predict_pydantic_validation():
    headers = {"Authorization": "Bearer mock_valid_token_prod_user_01"}

    # Invalid social_media_ratio > 1.0
    invalid_payload = {
        "switch_frequency_5m": 5.0,
        "social_media_ratio": 2.5, # Out of range
        "entertainment_ratio": 0.0
    }

    res = client.post("/api/ml/predict", json=invalid_payload, headers=headers)
    assert res.status_code == 422 # Pydantic Validation Error

def test_production_ml_predict_unauthorized():
    res = client.post("/api/ml/predict", json={})
    assert res.status_code == 401
