from fastapi.testclient import TestClient
from main import app
from services.heuristics import FeatureAggregator, BehavioralHeuristicScorer
from core.categories import category_registry

client = TestClient(app)

def test_feature_aggregation():
    events = [
        {
            "website_domain": "github.com",
            "session_duration": 60,
            "app_switch_count": 2,
            "browser_switch_count": 1,
            "notification_count": 0,
            "idle_seconds": 0
        },
        {
            "website_domain": "twitter.com",
            "session_duration": 120,
            "app_switch_count": 5,
            "browser_switch_count": 4,
            "notification_count": 2,
            "idle_seconds": 30
        }
    ]

    features = FeatureAggregator.aggregate_features("user_test_1", events)
    assert features["session_duration"] == 180
    assert features["total_switches"] == 12
    assert features["social_media_duration"] == 120
    assert features["productive_duration"] == 60

def test_heuristic_scorer_explanation():
    events = [
        {
            "website_domain": "twitter.com",
            "session_duration": 150,
            "app_switch_count": 6,
            "browser_switch_count": 5,
            "notification_count": 4,
            "idle_seconds": 0
        }
    ]

    score_res = BehavioralHeuristicScorer.evaluate_focus_score("user_test_2", events)
    assert score_res["evaluation_type"] == "heuristic"
    assert score_res["score_value"] < 70.0
    assert "switched contexts" in score_res["explanation"]
    assert "social media domains" in score_res["explanation"]

def test_configurable_categories_api():
    headers = {"Authorization": "Bearer mock_valid_token_user_789"}

    # Configure youtube.com as productive for user 789
    res_config = client.post(
        "/api/categories",
        json={"item_name": "youtube.com", "category": "productive", "is_domain": True},
        headers=headers
    )
    assert res_config.status_code == 200
    assert res_config.json()["assigned_category"] == "productive"

    # Verify custom mapping retrieved in GET /api/categories
    res_get = client.get("/api/categories", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["custom_domain_overrides"]["youtube.com"] == "productive"

def test_focus_evaluate_api():
    headers = {"Authorization": "Bearer mock_valid_token_user_789"}

    # Ingest event
    client.post(
        "/api/events",
        json={
            "website_domain": "github.com",
            "session_duration": 300,
            "app_switch_count": 1,
            "browser_switch_count": 0
        },
        headers=headers
    )

    # Evaluate score
    res_eval = client.post("/api/focus/evaluate", headers=headers)
    assert res_eval.status_code == 200
    score_data = res_eval.json()["score"]
    assert "score_value" in score_data
    assert "explanation" in score_data
    assert score_data["evaluation_type"] == "heuristic"
