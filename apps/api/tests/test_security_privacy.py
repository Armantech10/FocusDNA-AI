from fastapi.testclient import TestClient
from main import app
from routers.sessions import user_sessions_store
from routers.events import user_events_db

client = TestClient(app)

def test_export_user_data():
    user_id = "sec_test_user_1"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    # Populate mock data
    user_sessions_store[user_id] = [{"id": "s1", "session_name": "Coding"}]
    user_events_db[user_id] = [{"id": "e1", "category": "Development"}]

    res = client.get("/api/privacy/export", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "export_metadata" in data
    assert data["export_metadata"]["user_id"] == user_id
    assert data["focus_sessions_count"] == 1
    assert data["activity_events_count"] == 1

def test_purge_user_data():
    user_id = "sec_test_user_2"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    user_sessions_store[user_id] = [{"id": "s1"}]
    user_events_db[user_id] = [{"id": "e1"}]

    res = client.post("/api/privacy/purge", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "data_purged"

    # Verify DB state is empty
    assert len(user_sessions_store[user_id]) == 0
    assert len(user_events_db[user_id]) == 0

def test_revoke_consent():
    user_id = "sec_test_user_3"
    headers = {"Authorization": f"Bearer mock_valid_token_{user_id}"}

    res = client.post("/api/privacy/revoke", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "consent_revoked"

def test_user_data_export_isolation():
    user_a = "sec_user_A"
    user_b = "sec_user_B"

    user_sessions_store[user_a] = [{"id": "s_A", "session_name": "Private A"}]
    user_sessions_store[user_b] = [{"id": "s_B", "session_name": "Private B"}]

    headers_a = {"Authorization": f"Bearer mock_valid_token_{user_a}"}
    res = client.get("/api/privacy/export", headers=headers_a)
    assert res.status_code == 200
    data = res.json()

    # User A should only see Session A
    assert data["focus_sessions_count"] == 1
    assert data["focus_sessions"][0]["session_name"] == "Private A"
