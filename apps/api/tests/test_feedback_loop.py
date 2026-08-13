from fastapi.testclient import TestClient
from main import app
from routers.feedback import feedback_db

client = TestClient(app)

def test_feedback_ingestion():
    user_id = "fb_test_user_100"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    # Test all 5 required buttons
    buttons = ["helpful", "not_helpful", "was_actually_focused", "was_distracted", "dont_remind_again"]

    for btn in buttons:
        res = client.post(
            "/api/feedback",
            json={"prediction_id": f"pred_{btn}", "feedback_type": btn},
            headers=headers
        )
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "recorded"
        assert data["feedback"]["feedback_type"] == btn

    # Verify DB storage
    stored = feedback_db.get(user_id, [])
    assert len(stored) == 5

def test_feedback_analytics_calculation():
    user_id = "fb_test_user_200"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    # Ingest 3 helpful, 1 false positive (was_actually_focused), 1 false negative (was_distracted)
    client.post("/api/feedback", json={"prediction_id": "p1", "feedback_type": "helpful"}, headers=headers)
    client.post("/api/feedback", json={"prediction_id": "p2", "feedback_type": "helpful"}, headers=headers)
    client.post("/api/feedback", json={"prediction_id": "p3", "feedback_type": "helpful"}, headers=headers)
    client.post("/api/feedback", json={"prediction_id": "p4", "feedback_type": "was_actually_focused"}, headers=headers)
    client.post("/api/feedback", json={"prediction_id": "p5", "feedback_type": "was_distracted"}, headers=headers)

    res = client.get("/api/feedback/analytics", headers=headers)
    assert res.status_code == 200
    analytics = res.json()

    assert analytics["has_feedback"] is True
    assert analytics["false_positives"] == 1
    assert analytics["false_negatives"] == 1
    assert analytics["prediction_accuracy"] == 60.0 # 3 helpful out of 5 total evaluated = 60.0%
    assert analytics["user_feedback_rate"] > 0

def test_controlled_retraining_endpoint():
    user_id = "fb_test_user_300"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    res = client.post("/api/feedback/retrain", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pipeline_executed"
    assert "pipeline_result" in data
    assert data["pipeline_result"]["passed_evaluation_gates"] is True

def test_invalid_feedback_type():
    headers = {"Authorization": "Bearer mock_valid_token_user_bad"}
    res = client.post("/api/feedback", json={"feedback_type": "invalid_button"}, headers=headers)
    assert res.status_code == 422
