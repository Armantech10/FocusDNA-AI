import pytest
from ml.feature_schema import CanonicalFeatureExtractor, CANONICAL_FEATURES, FEATURE_SCHEMA_VERSION

def test_canonical_feature_extraction():
    events = [
        {"website_domain": "github.com", "session_duration": 120, "browser_switch_count": 2, "idle_seconds": 10},
        {"website_domain": "twitter.com", "session_duration": 180, "browser_switch_count": 4, "idle_seconds": 20}
    ]
    session_meta = {"planned_duration_minutes": 25, "actual_duration_minutes": 25, "started_at": "2026-08-20T14:30:00Z"}

    feats = CanonicalFeatureExtractor.extract_features(events, session_meta)

    assert len(feats) == 13
    assert set(feats.keys()) == set(CANONICAL_FEATURES)
    assert feats["browser_switch_count"] == 6
    assert feats["social_media_duration_minutes"] == 3.0
    assert feats["productive_duration_minutes"] == 2.0
    assert feats["time_of_day_hour"] == 14
    assert feats["day_of_week"] == 3  # Aug 20 2026 is Thursday (0=Mon, 3=Thu)

def test_canonical_dataframe_ordering():
    events = [{"website_domain": "google.com", "session_duration": 60}]
    feats = CanonicalFeatureExtractor.extract_features(events)
    df = CanonicalFeatureExtractor.to_dataframe(feats)

    assert list(df.columns) == CANONICAL_FEATURES
    assert df.shape == (1, 13)
