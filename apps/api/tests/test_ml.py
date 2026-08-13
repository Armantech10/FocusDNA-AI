import os
from fastapi.testclient import TestClient
from main import app
from services.ml_service import ml_service
from ml.models.comparator import run_model_comparison

client = TestClient(app)

def test_model_comparison_execution():
    artifact = run_model_comparison()
    assert "model_name" in artifact
    assert "f1_score" in artifact
    assert artifact["f1_score"] > 0.8
    assert os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/reports/model_comparison_report.md")))

def test_ml_service_inference():
    sample_features = {
        "switch_frequency_5m": 12,
        "social_media_ratio": 0.45,
        "entertainment_ratio": 0.10,
        "idle_ratio": 0.05,
        "session_elapsed_minutes": 65,
        "time_of_day_hour": 15
    }

    prediction = ml_service.predict_attention_loss(sample_features)
    assert "risk_probability" in prediction
    assert 0.0 <= prediction["risk_probability"] <= 1.0
    assert "ML Predictive Model" in prediction["attribution_label"]
    assert len(prediction["primary_drivers"]) > 0

def test_predict_attention_loss_api():
    headers = {"Authorization": "Bearer mock_valid_token_user_ml_99"}

    res_low = client.post(
        "/api/predict/attention-loss",
        json={
            "switch_frequency_5m": 1,
            "social_media_ratio": 0.0,
            "entertainment_ratio": 0.0,
            "idle_ratio": 0.0,
            "session_elapsed_minutes": 10,
            "time_of_day_hour": 10
        },
        headers=headers
    )
    assert res_low.status_code == 200
    pred_low = res_low.json()["prediction"]
    assert pred_low["risk_level"] in ["Low Risk", "Moderate Risk", "High Risk"]

def test_isolation_forest_anomaly_api():
    headers = {"Authorization": "Bearer mock_valid_token_user_ml_99"}

    # Normal behavior (10m entertainment)
    res_normal = client.post(
        "/api/predict/anomaly",
        json={"entertainment_duration_minutes": 10.0, "switch_frequency_5m": 3, "idle_seconds": 15},
        headers=headers
    )
    assert res_normal.status_code == 200
    assert res_normal.json()["anomaly"]["is_anomaly"] is False

    # Anomalous behavior (90m YouTube spike)
    res_anomaly = client.post(
        "/api/predict/anomaly",
        json={"entertainment_duration_minutes": 90.0, "switch_frequency_5m": 12, "idle_seconds": 60},
        headers=headers
    )
    assert res_anomaly.status_code == 200
    anomaly_data = res_anomaly.json()["anomaly"]
    assert anomaly_data["is_anomaly"] is True
    assert anomaly_data["model_type"] == "IsolationForest"
    assert "90 minutes" in anomaly_data["explanation"]
