from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_unauthorized_access_rejected():
    # Attempting to access protected endpoints without auth token should return 401
    response = client.get("/api/profile")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]

    response_events = client.get("/api/events")
    assert response_events.status_code == 401

def test_authenticated_profile_access():
    headers = {"Authorization": "Bearer mock_valid_token_user_123"}
    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["profile"]["user_id"] == "user_123"

def test_user_data_isolation():
    headers_user1 = {"Authorization": "Bearer mock_valid_token_user_123"}
    headers_user2 = {"Authorization": "Bearer mock_valid_token_user_456"}

    # User 1 inserts an event
    payload1 = {
        "application_name": "Visual Studio Code",
        "website_domain": "github.com",
        "session_duration": 120
    }
    res_insert1 = client.post("/api/events", json=payload1, headers=headers_user1)
    assert res_insert1.status_code == 201

    # User 2 queries their own events - should NOT see User 1's event
    res_get2 = client.get("/api/events", headers=headers_user2)
    assert res_get2.status_code == 200
    assert res_get2.json()["count"] == 0

    # User 1 queries their own events - SHOULD see their 1 event
    res_get1 = client.get("/api/events", headers=headers_user1)
    assert res_get1.status_code == 200
    assert res_get1.json()["count"] == 1
    assert res_get1.json()["events"][0]["application_name"] == "Visual Studio Code"
