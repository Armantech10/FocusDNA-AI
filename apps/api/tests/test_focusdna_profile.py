from fastapi.testclient import TestClient
from main import app
from routers.sessions import user_sessions_store
from routers.events import user_events_db

client = TestClient(app)

def test_focusdna_profile_insufficient_data():
    headers = {"Authorization": "Bearer mock_valid_token_fresh_user_100"}

    # Fresh user with 0 sessions and 0 events
    res = client.get("/api/profile/focusdna", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["has_sufficient_data"] is False
    assert data["profile"] is None
    assert data["message"] == "Keep using FocusDNA to build your profile."

def test_focusdna_profile_with_real_history():
    user_id = "user_focusdna_test_200"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    # Populate 3 completed sessions & 3 activity events
    user_sessions_store[user_id] = [
        {
            "id": "s1",
            "session_name": "Deep Coding",
            "status": "completed",
            "actual_duration_minutes": 40,
            "distraction_count": 2,
            "app_switch_count": 3,
            "started_at": "2026-08-13T09:15:00Z"
        },
        {
            "id": "s2",
            "session_name": "API Architecture",
            "status": "completed",
            "actual_duration_minutes": 44,
            "distraction_count": 1,
            "app_switch_count": 4,
            "started_at": "2026-08-13T10:00:00Z"
        },
        {
            "id": "s3",
            "session_name": "Interrupted",
            "status": "canceled",
            "actual_duration_minutes": 10,
            "distraction_count": 5,
            "app_switch_count": 8,
            "started_at": "2026-08-13T14:30:00Z"
        }
    ]

    user_events_db[user_id] = [
        {"id": "e1", "category": "Social Media", "app_switch_count": 3, "timestamp": "2026-08-13T14:35:00Z"},
        {"id": "e2", "category": "Social Media", "app_switch_count": 4, "timestamp": "2026-08-13T14:40:00Z"},
        {"id": "e3", "category": "Development", "app_switch_count": 1, "timestamp": "2026-08-13T09:20:00Z"}
    ]

    res = client.get("/api/profile/focusdna", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["has_sufficient_data"] is True
    prof = data["profile"]
    assert prof["typical_session_minutes"] == 42 # Mean of 40 and 44 = 42 min
    assert prof["focus_consistency"] == 67 # 2 completed out of 3 total = 67%
    assert prof["average_context_switches"] > 0
    assert prof["most_common_trigger"] == "Social Media"
    assert "AM" in prof["best_focus_period"] or "PM" in prof["best_focus_period"]
