"""
FocusDNA AI — Canonical Feature Schema (Phase 1)
Single authoritative feature definition used identically across:
- Training
- Validation
- Testing
- Production Inference
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

FEATURE_SCHEMA_VERSION = "1.0"

CANONICAL_FEATURES: List[str] = [
    "total_duration_minutes",
    "app_switch_count",
    "browser_switch_count",
    "idle_minutes",
    "social_media_duration_minutes",
    "entertainment_duration_minutes",
    "productive_duration_minutes",
    "context_switch_frequency",
    "distraction_ratio",
    "active_time_ratio",
    "session_completion_ratio",
    "time_of_day_hour",
    "day_of_week"
]

FEATURE_BOUNDS: Dict[str, tuple] = {
    "total_duration_minutes": (0.0, 300.0),
    "app_switch_count": (0, 500),
    "browser_switch_count": (0, 500),
    "idle_minutes": (0.0, 300.0),
    "social_media_duration_minutes": (0.0, 300.0),
    "entertainment_duration_minutes": (0.0, 300.0),
    "productive_duration_minutes": (0.0, 300.0),
    "context_switch_frequency": (0.0, 100.0),
    "distraction_ratio": (0.0, 1.0),
    "active_time_ratio": (0.0, 1.0),
    "session_completion_ratio": (0.0, 2.0),
    "time_of_day_hour": (0, 23),
    "day_of_week": (0, 6)
}

class CanonicalFeatureExtractor:
    @staticmethod
    def extract_features(
        telemetry_events: Any = None,
        session_meta: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Extracts canonical 13-feature vector from raw telemetry events, dictionary, or session metadata.
        Guarantees exact feature ordering, type casting, bounds clipping, and NaN safety.
        """
        session_meta = session_meta or {}

        # If telemetry_events is passed directly as a feature dictionary (legacy API caller)
        if isinstance(telemetry_events, dict):
            input_dict = telemetry_events
            features = {
                "total_duration_minutes": float(input_dict.get("total_duration_minutes", input_dict.get("session_elapsed_minutes", session_meta.get("actual_duration_minutes", 25.0)))),
                "app_switch_count": int(input_dict.get("app_switch_count", 0)),
                "browser_switch_count": int(input_dict.get("browser_switch_count", input_dict.get("total_switches", 0))),
                "idle_minutes": float(input_dict.get("idle_minutes", round(float(input_dict.get("idle_seconds", 0)) / 60.0, 2))),
                "social_media_duration_minutes": float(input_dict.get("social_media_duration_minutes", input_dict.get("social_media_duration", 0.0))),
                "entertainment_duration_minutes": float(input_dict.get("entertainment_duration_minutes", input_dict.get("entertainment_duration", 0.0))),
                "productive_duration_minutes": float(input_dict.get("productive_duration_minutes", input_dict.get("productive_duration", 0.0))),
                "context_switch_frequency": float(input_dict.get("context_switch_frequency", input_dict.get("switch_frequency_5m", 0.0))),
                "distraction_ratio": float(input_dict.get("distraction_ratio", input_dict.get("social_media_ratio", 0.0) + input_dict.get("entertainment_ratio", 0.0))),
                "active_time_ratio": float(input_dict.get("active_time_ratio", 1.0 - float(input_dict.get("idle_ratio", 0.0)))),
                "session_completion_ratio": float(input_dict.get("session_completion_ratio", 1.0)),
                "time_of_day_hour": int(input_dict.get("time_of_day_hour", 14)),
                "day_of_week": int(input_dict.get("day_of_week", 2))
            }
            for feat, val in features.items():
                if np.isnan(val):
                    val = 0.0
                min_v, max_v = FEATURE_BOUNDS[feat]
                features[feat] = type(val)(max(min_v, min(max_v, val)))
            return features

        events_list = telemetry_events if isinstance(telemetry_events, list) else []

        planned_duration = float(session_meta.get("planned_duration_minutes", session_meta.get("target_duration_minutes", 25.0)))
        actual_duration = float(session_meta.get("actual_duration_minutes", session_meta.get("duration", 0.0)))
        
        # Calculate raw aggregates from telemetry events
        total_event_duration = sum(float(e.get("session_duration", 30)) for e in events_list)
        total_duration_mins = max(actual_duration, round(total_event_duration / 60.0, 2))
        if total_duration_mins <= 0.0:
            total_duration_mins = planned_duration

        app_switches = sum(int(e.get("app_switch_count", 0)) for e in events_list)
        browser_switches = sum(int(e.get("browser_switch_count", 0)) for e in events_list)
        idle_secs = sum(float(e.get("idle_seconds", 0)) for e in events_list)
        idle_mins = round(idle_secs / 60.0, 2)

        social_secs = 0.0
        ent_secs = 0.0
        prod_secs = 0.0

        for e in events_list:
            domain = (e.get("website_domain") or "").lower()
            dur = float(e.get("session_duration", 30))
            if any(s in domain for s in ["twitter.com", "x.com", "instagram.com", "facebook.com", "reddit.com", "tiktok.com"]):
                social_secs += dur
            elif any(s in domain for s in ["youtube.com", "netflix.com", "twitch.tv", "hulu.com"]):
                ent_secs += dur
            else:
                prod_secs += dur

        social_mins = round(social_secs / 60.0, 2)
        ent_mins = round(ent_secs / 60.0, 2)
        prod_mins = round(prod_secs / 60.0, 2)

        total_switches = app_switches + browser_switches
        context_switch_freq = round((total_switches / max(1.0, total_duration_mins)) * 5.0, 2)

        distraction_secs = social_secs + ent_secs
        distraction_ratio = round(distraction_secs / max(1.0, total_event_duration), 3) if total_event_duration > 0 else 0.0
        
        active_secs = max(0.0, (total_duration_mins * 60.0) - idle_secs)
        active_time_ratio = round(active_secs / max(1.0, total_duration_mins * 60.0), 3)

        completion_ratio = round(actual_duration / max(1.0, planned_duration), 2) if actual_duration > 0 else 1.0

        timestamp_str = session_meta.get("started_at", session_meta.get("timestamp"))
        if timestamp_str:
            try:
                dt = pd.to_datetime(timestamp_str)
                hour = dt.hour
                dow = dt.dayofweek
            except Exception:
                hour = 14
                dow = 2
        else:
            hour = 14
            dow = 2

        features = {
            "total_duration_minutes": total_duration_mins,
            "app_switch_count": app_switches,
            "browser_switch_count": browser_switches,
            "idle_minutes": idle_mins,
            "social_media_duration_minutes": social_mins,
            "entertainment_duration_minutes": ent_mins,
            "productive_duration_minutes": prod_mins,
            "context_switch_frequency": context_switch_freq,
            "distraction_ratio": distraction_ratio,
            "active_time_ratio": active_time_ratio,
            "session_completion_ratio": completion_ratio,
            "time_of_day_hour": hour,
            "day_of_week": dow
        }

        # Enforce clipping bounds & NaN checks
        for feat, val in features.items():
            if np.isnan(val):
                val = 0.0
            min_v, max_v = FEATURE_BOUNDS[feat]
            features[feat] = type(val)(max(min_v, min(max_v, val)))

        return features

    @staticmethod
    def to_dataframe(features_dict: Dict[str, Any]) -> pd.DataFrame:
        """
        Converts feature dictionary into DataFrame matching exact CANONICAL_FEATURES order.
        """
        df = pd.DataFrame([features_dict])
        for col in CANONICAL_FEATURES:
            if col not in df.columns:
                df[col] = 0.0
        return df[CANONICAL_FEATURES]
