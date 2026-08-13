from fastapi.testclient import TestClient
from main import app
from services.gemini_service import gemini_service

client = TestClient(app)

def test_ai_recommendation_endpoint_schema():
    headers = {"Authorization": "Bearer mock_valid_token_ai_user_01"}

    payload = {
        "average_focus_session": 42.0,
        "common_distraction_period": "9:00 AM – 11:00 AM",
        "average_switches": 3.2,
        "top_trigger": "Social Media",
        "recent_anomaly": False,
        "focus_trend": "improving"
    }

    res = client.post("/api/ai/recommendation", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "explanation" in data
    assert "recommendation" in data
    assert "suggested_intervention" in data
    assert "cached" in data
    assert "source" in data

    # Verify example format requirements
    assert "focus" in data["explanation"].lower() or "session" in data["explanation"].lower()
    assert len(data["suggested_intervention"]) > 10

def test_ai_recommendation_caching():
    user_id = "ai_cache_test_user_99"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}
    payload = {"average_focus_session": 40.0, "top_trigger": "Video Streaming"}

    # First request -> fresh
    res1 = client.post("/api/ai/recommendation", json=payload, headers=headers)
    assert res1.status_code == 200
    assert res1.json()["cached"] is False

    # Second request -> cached
    res2 = client.post("/api/ai/recommendation", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["cached"] is True

def test_ai_recommendation_rate_limiting():
    user_id = "ai_rate_limit_user_77"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    # Reset timestamps for clean test
    gemini_service.user_request_timestamps[user_id] = []

    # Send 10 requests -> allowed
    for i in range(10):
        res = client.post("/api/ai/recommendation", json={"average_focus_session": 30 + i}, headers=headers)
        assert res.status_code == 200

    # 11th request -> HTTP 429
    res_exceeded = client.post("/api/ai/recommendation", json={"average_focus_session": 99}, headers=headers)
    assert res_exceeded.status_code == 429

def test_ai_recommendation_unauthorized():
    res = client.post("/api/ai/recommendation", json={})
    assert res.status_code == 401
