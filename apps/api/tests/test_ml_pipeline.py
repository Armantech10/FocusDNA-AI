import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from main import app

from ml.feature_schema import CanonicalFeatureExtractor, CANONICAL_FEATURES, FEATURE_SCHEMA_VERSION
from ml.data_validation import DataQualityValidator
from ml.dataset import DatasetManager
from ml.calibration import ProbabilityCalibrator
from ml.model_registry import model_registry
from ml.personalization import personalized_engine
from ml.drift import FeatureDriftDetector
from ml.monitoring import ml_monitor
from apps.api.services.ml_service import ml_service

client = TestClient(app)

def test_data_quality_validator():
    events = [
        {"id": "ev_1", "session_duration": 60, "idle_seconds": 5},
        {"id": "ev_2", "session_duration": 120, "idle_seconds": 10}
    ]
    session_meta = {"planned_duration_minutes": 25, "actual_duration_minutes": 20}

    is_valid, issues = DataQualityValidator.validate_session_telemetry(events, session_meta)
    assert is_valid is True
    assert len(issues) == 0

def test_data_quality_validator_invalid():
    events = [{"id": "ev_1", "session_duration": -10, "idle_seconds": 5}]
    is_valid, issues = DataQualityValidator.validate_session_telemetry(events)
    assert is_valid is False
    assert len(issues) > 0

def test_leakage_safe_splitting():
    X, y, meta = DatasetManager.generate_prototype_baseline_dataset(num_samples=100, random_seed=42)
    splits = DatasetManager.split_leakage_safe(X, y, meta, test_size=0.2, val_size=0.1, method="time_aware")

    assert len(splits["X_train"]) > 0
    assert len(splits["X_val"]) > 0
    assert len(splits["X_test"]) > 0
    assert splits["leakage_check_passed"] is True

def test_probability_calibrator():
    cal = ProbabilityCalibrator()
    raw_probs = np.array([0.1, 0.4, 0.7, 0.9])
    y_true = np.array([0, 0, 1, 1])

    cal.fit(raw_probs, y_true)
    assert cal.is_fitted is True

    cal_probs = cal.predict_proba(raw_probs)
    assert len(cal_probs) == 4
    assert all(0.0 <= p <= 1.0 for p in cal_probs)

def test_model_registry_lifecycle():
    prod_info = model_registry.get_production_model_info()
    assert prod_info is not None
    assert "model_version" in prod_info
    assert prod_info["feature_schema_version"] == "1.0"

def test_personalization_thresholds():
    empty_history = []
    base_info = personalized_engine.compute_user_baseline(empty_history)
    assert base_info["personalization_status"] == "insufficient_data"

    adj = personalized_engine.adjust_prediction(0.8, {"context_switch_frequency": 8.0}, base_info)
    assert adj["personalization_applied"] is False
    assert adj["final_probability"] == 0.8

def test_production_ml_inference_service():
    events = [
        {"website_domain": "github.com", "session_duration": 300, "browser_switch_count": 2, "idle_seconds": 10},
        {"website_domain": "twitter.com", "session_duration": 180, "browser_switch_count": 6, "idle_seconds": 5}
    ]
    res = ml_service.predict_production_ml(telemetry_events=events, session_meta={"planned_duration_minutes": 25})

    assert "prediction" in res
    assert "attention_loss_probability" in res
    assert "confidence" in res
    assert res["feature_schema_version"] == "1.0"
    assert "top_explanatory_factors" in res
    assert "model_notice" in res
    assert res["dataset_type"] == "synthetic_baseline"

def test_drift_detector():
    np.random.seed(42)
    ref = pd.DataFrame({"context_switch_frequency": np.linspace(1, 10, 100)})
    curr = pd.DataFrame({"context_switch_frequency": np.linspace(1, 10, 100)})

    res = FeatureDriftDetector.evaluate_feature_drift(ref, curr)
    assert "drift_detected" in res
    assert res["drift_detected"] is False

def test_ml_monitoring_endpoints():
    headers = {"Authorization": "Bearer mock_valid_token_user_ml_mon"}

    res_status = client.get("/api/ml/status", headers=headers)
    assert res_status.status_code == 200
    st_data = res_status.json()
    assert st_data["readiness_status"] == "PRODUCTION ML INFRASTRUCTURE READY"
    assert "PROTOTYPE BASELINE MODEL" in st_data["model_status"]

    res_mon = client.get("/api/ml/monitoring", headers=headers)
    assert res_mon.status_code == 200

    res_drift = client.get("/api/ml/drift", headers=headers)
    assert res_drift.status_code == 200
