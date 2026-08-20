from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_session_lifecycle():
    headers = {"Authorization": "Bearer mock_valid_token_user_123"}

    # 1. Start Session
    res_start = client.post(
        "/api/sessions/start",
        json={"session_name": "25m Deep Work", "planned_duration_minutes": 25},
        headers=headers
    )
    assert res_start.status_code == 201
    session_id = res_start.json()["session"]["id"]
    assert res_start.json()["session"]["status"] == "active"
    assert res_start.json()["session"]["planned_duration"] == 25

    # 2. Pause Session
    res_pause = client.post(
        "/api/sessions/pause",
        json={"session_id": session_id, "distraction_count": 1, "actual_duration_minutes": 10},
        headers=headers
    )
    assert res_pause.status_code == 200
    assert res_pause.json()["session"]["status"] == "paused"

    # 3. Resume Session
    res_resume = client.post(
        "/api/sessions/resume",
        json={"session_id": session_id},
        headers=headers
    )
    assert res_resume.status_code == 200
    assert res_resume.json()["session"]["status"] == "active"

    # 4. Finish Session
    res_finish = client.post(
        "/api/sessions/finish",
        json={"session_id": session_id, "distraction_count": 1, "actual_duration_minutes": 25},
        headers=headers
    )
    assert res_finish.status_code == 200
    finished_data = res_finish.json()
    assert finished_data["status"] == "finished"
    assert finished_data["session"]["completed"] is True
    assert "heuristic_score" in finished_data["session"]
    assert finished_data["session"]["heuristic_score"]["attribution"] == "Heuristic Focus Score"

def test_session_cancel():
    headers = {"Authorization": "Bearer mock_valid_token_user_123"}

    # Start and cancel session
    res_start = client.post(
        "/api/sessions/start",
        json={"session_name": "Short Session", "planned_duration_minutes": 15},
        headers=headers
    )
    session_id = res_start.json()["session"]["id"]

    res_cancel = client.post(
        "/api/sessions/cancel",
        json={"session_id": session_id, "distraction_count": 0, "actual_duration_minutes": 5},
        headers=headers
    )
    assert res_cancel.status_code == 200
    assert res_cancel.json()["session"]["status"] == "canceled"
    assert res_cancel.json()["session"]["completed"] is False

def test_session_history_isolation():
    headers_user1 = {"Authorization": "Bearer mock_valid_token_user_123"}
    headers_user2 = {"Authorization": "Bearer mock_valid_token_user_456"}

    # Check history for user 2
    res_h2 = client.get("/api/sessions/history", headers=headers_user2)
    assert res_h2.status_code == 200
    assert res_h2.json()["total_sessions"] == 0

    # User 1 history should contain their sessions
    res_h1 = client.get("/api/sessions/history", headers=headers_user1)
    assert res_h1.status_code == 200
    assert res_h1.json()["total_sessions"] >= 2

def test_telemetry_session_id_sync():
    headers = {"Authorization": "Bearer mock_valid_token_user_e2e"}

    # 1. Start Session
    res_start = client.post(
        "/api/sessions/start",
        json={"session_name": "E2E Telemetry Session", "planned_duration_minutes": 25},
        headers=headers
    )
    assert res_start.status_code == 201
    session_id = res_start.json()["session"]["id"]

    # 2. Ingest Extension Telemetry associated with this focus_session_id
    res_event1 = client.post(
        "/api/events",
        json={
            "website_domain": "github.com",
            "application_name": "Google Chrome",
            "session_duration": 120,
            "browser_switch_count": 3,
            "app_switch_count": 0,
            "idle_seconds": 5,
            "typing_activity_level": "medium",
            "device_type": "browser_extension",
            "focus_session_id": session_id
        },
        headers=headers
    )
    assert res_event1.status_code == 201

    res_event2 = client.post(
        "/api/events",
        json={
            "website_domain": "twitter.com",
            "application_name": "Google Chrome",
            "session_duration": 180,
            "browser_switch_count": 5,
            "app_switch_count": 0,
            "idle_seconds": 0,
            "typing_activity_level": "medium",
            "device_type": "browser_extension",
            "focus_session_id": session_id
        },
        headers=headers
    )
    assert res_event2.status_code == 201

    # 3. Retrieve events filtered by focus_session_id
    res_get = client.get(f"/api/events?focus_session_id={session_id}", headers=headers)
    assert res_get.status_code == 200
    events = res_get.json()["events"]
    assert len(events) == 2
    assert all(e["focus_session_id"] == session_id for e in events)

    # 4. Finish session and verify session-linked telemetry evaluation
    res_finish = client.post(
        "/api/sessions/finish",
        json={"session_id": session_id, "distraction_count": 0, "actual_duration_minutes": 5},
        headers=headers
    )
    assert res_finish.status_code == 200
    fin = res_finish.json()
    assert fin["telemetry_evaluated"]["has_real_telemetry"] is True
    assert fin["telemetry_evaluated"]["event_count"] == 2

