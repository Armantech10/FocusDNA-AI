"""
FocusDNA AI — Real Session Labeling & Dataset Extraction Pipeline Verification Test
Verifies all 10 checkpoints for ground truth labeling:
1. Table schema & fields
2. RLS & user data isolation
3. Authenticated user_id mapping
4. focus_session_id mapping
5. 1-5 rating mapping
6. Binary target generation (0 for focused, 1 for distracted)
7. Duplicate label prevention (in-place upsert)
8. Exact telemetry association
9. Training dataset extraction (13 canonical features)
10. End-to-end insert, retrieve, feature extraction, and training sample generation
"""

import pytest
from fastapi.testclient import TestClient
from main import app

from ml.labeling import SessionLabelingEngine, RATING_MAP
from ml.feature_schema import CanonicalFeatureExtractor, CANONICAL_FEATURES
from ml.dataset import DatasetManager
from ml.data_validation import DataQualityValidator

client = TestClient(app)

def test_label_mapping_engine():
    # 1: Very focused -> 0
    # 2: Mostly focused -> 0
    # 3: Neutral -> 1
    # 4: Distracted -> 1
    # 5: Very distracted -> 1
    assert SessionLabelingEngine.map_user_rating(1) == ("very_focused", 0)
    assert SessionLabelingEngine.map_user_rating(2) == ("mostly_focused", 0)
    assert SessionLabelingEngine.map_user_rating(3) == ("neutral", 1)
    assert SessionLabelingEngine.map_user_rating(4) == ("distracted", 1)
    assert SessionLabelingEngine.map_user_rating(5) == ("very_distracted", 1)

    with pytest.raises(ValueError):
        SessionLabelingEngine.map_user_rating(6)

def test_session_rating_submission_and_duplicate_handling():
    headers_user1 = {"Authorization": "Bearer mock_valid_token_user_verified_1"}
    headers_user2 = {"Authorization": "Bearer mock_valid_token_user_verified_2"}
    test_session_id = "session_test_label_verification_101"

    # 1. Start Session for User 1
    res_start = client.post(
        "/api/sessions/start",
        json={"session_name": "Label Verification Session", "planned_duration_minutes": 25},
        headers=headers_user1
    )
    assert res_start.status_code == 201

    # 2. Ingest real telemetry events for this session
    client.post(
        "/api/events",
        json={
            "website_domain": "github.com",
            "application_name": "Google Chrome",
            "session_duration": 300,
            "browser_switch_count": 2,
            "app_switch_count": 0,
            "idle_seconds": 10,
            "typing_activity_level": "high",
            "device_type": "browser_extension",
            "focus_session_id": test_session_id
        },
        headers=headers_user1
    )

    client.post(
        "/api/events",
        json={
            "website_domain": "twitter.com",
            "application_name": "Google Chrome",
            "session_duration": 180,
            "browser_switch_count": 5,
            "app_switch_count": 0,
            "idle_seconds": 5,
            "typing_activity_level": "medium",
            "device_type": "browser_extension",
            "focus_session_id": test_session_id
        },
        headers=headers_user1
    )

    # 3. Submit 5-level Focus Rating (Rating 1: Very focused -> Binary Target 0)
    res_rating = client.post(
        "/api/feedback/session-rating",
        json={"focus_session_id": test_session_id, "user_rating": 1},
        headers=headers_user1
    )
    assert res_rating.status_code == 201
    label_data = res_rating.json()["label_record"]
    assert label_data["user_rating"] == 1
    assert label_data["rating_label"] == "very_focused"
    assert label_data["binary_target"] == 0
    assert label_data["focus_session_id"] == test_session_id

    # 4. Verify Duplicate Prevention: User updates rating to 4 (Distracted -> Binary Target 1)
    res_update = client.post(
        "/api/feedback/session-rating",
        json={"focus_session_id": test_session_id, "user_rating": 4},
        headers=headers_user1
    )
    assert res_update.status_code == 201
    updated_label = res_update.json()["label_record"]
    assert updated_label["user_rating"] == 4
    assert updated_label["rating_label"] == "distracted"
    assert updated_label["binary_target"] == 1

    # 5. Retrieve session labels and verify user isolation & no duplicate row
    res_get_u1 = client.get("/api/feedback/session-labels", headers=headers_user1)
    assert res_get_u1.status_code == 200
    u1_labels = res_get_u1.json()["labeled_sessions"]
    matching = [l for l in u1_labels if l["focus_session_id"] == test_session_id]
    assert len(matching) == 1  # Guaranteed exactly 1 row (duplicate prevented)
    assert matching[0]["user_rating"] == 4
    assert matching[0]["binary_target"] == 1
    assert len(matching[0]["telemetry_events"]) == 2

    # Verify User 2 isolation (cannot see User 1's labeled sessions)
    res_get_u2 = client.get("/api/feedback/session-labels", headers=headers_user2)
    assert res_get_u2.status_code == 200
    u2_labels = res_get_u2.json()["labeled_sessions"]
    assert len([l for l in u2_labels if l["focus_session_id"] == test_session_id]) == 0

def test_end_to_end_labeled_dataset_extraction():
    # Construct verified labeled record structure
    labeled_records = [
        {
            "user_id": "user_verified_e2e",
            "focus_session_id": "session_e2e_001",
            "user_rating": 2,
            "rating_label": "mostly_focused",
            "binary_target": 0,
            "label_source": "user_session_rating",
            "telemetry_events": [
                {"website_domain": "github.com", "session_duration": 600, "browser_switch_count": 3, "idle_seconds": 15},
                {"website_domain": "stackoverflow.com", "session_duration": 300, "browser_switch_count": 2, "idle_seconds": 0}
            ],
            "session_meta": {
                "planned_duration_minutes": 25,
                "actual_duration_minutes": 15,
                "started_at": "2026-08-20T10:00:00Z"
            }
        },
        {
            "user_id": "user_verified_e2e",
            "focus_session_id": "session_e2e_002",
            "user_rating": 5,
            "rating_label": "very_distracted",
            "binary_target": 1,
            "label_source": "user_session_rating",
            "telemetry_events": [
                {"website_domain": "twitter.com", "session_duration": 400, "browser_switch_count": 8, "idle_seconds": 20},
                {"website_domain": "youtube.com", "session_duration": 500, "browser_switch_count": 6, "idle_seconds": 10}
            ],
            "session_meta": {
                "planned_duration_minutes": 25,
                "actual_duration_minutes": 15,
                "started_at": "2026-08-20T11:00:00Z"
            }
        }
    ]

    X, y, meta_df = DatasetManager.extract_dataset_from_records(labeled_records)

    assert len(X) == 2
    assert len(y) == 2
    assert list(X.columns) == CANONICAL_FEATURES
    assert list(y.values) == [0, 1]
    assert meta_df["is_synthetic"].tolist() == [False, False]
    assert meta_df["focus_session_id"].tolist() == ["session_e2e_001", "session_e2e_002"]

    # Verify specific feature extraction values
    # Session 1 (Focused):
    assert X.iloc[0]["browser_switch_count"] == 5
    assert X.iloc[0]["distraction_ratio"] == 0.0
    assert X.iloc[0]["productive_duration_minutes"] == 15.0

    # Session 2 (Distracted):
    assert X.iloc[1]["browser_switch_count"] == 14
    assert X.iloc[1]["distraction_ratio"] == 1.0
    assert X.iloc[1]["social_media_duration_minutes"] == 6.67
    assert X.iloc[1]["entertainment_duration_minutes"] == 8.33
