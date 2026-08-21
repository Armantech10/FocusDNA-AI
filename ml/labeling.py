"""
FocusDNA AI — Real Session Labeling Engine (Phase 2)
Maps human feedback and 5-point focus ratings into ground truth target representations.
"""

from typing import Dict, Any, Tuple

RATING_MAP = {
    1: ("very_focused", 0),
    2: ("mostly_focused", 0),
    3: ("neutral", 1),
    4: ("distracted", 1),
    5: ("very_distracted", 1)
}

FEEDBACK_TYPE_MAP = {
    "was_actually_focused": 0,
    "was_distracted": 1,
    "helpful": 0,
    "not_helpful": 1
}

class SessionLabelingEngine:
    @staticmethod
    def map_user_rating(user_rating: int) -> Tuple[str, int]:
        """
        Maps 1-5 integer rating to (rating_label, binary_target).
        1 (Very focused) -> ('very_focused', 0)
        2 (Mostly focused) -> ('mostly_focused', 0)
        3 (Neutral) -> ('neutral', 1)
        4 (Distracted) -> ('distracted', 1)
        5 (Very distracted) -> ('very_distracted', 1)
        """
        if user_rating not in RATING_MAP:
            raise ValueError(f"Invalid user_rating {user_rating}. Must be between 1 and 5.")
        return RATING_MAP[user_rating]

    @staticmethod
    def create_label_record(
        user_id: str,
        focus_session_id: str,
        user_rating: int,
        label_source: str = "user_session_rating"
    ) -> Dict[str, Any]:
        rating_label, binary_target = SessionLabelingEngine.map_user_rating(user_rating)
        return {
            "user_id": user_id,
            "focus_session_id": focus_session_id,
            "user_rating": user_rating,
            "rating_label": rating_label,
            "binary_target": binary_target,
            "label_source": label_source,
            "feature_schema_version": "1.0"
        }
