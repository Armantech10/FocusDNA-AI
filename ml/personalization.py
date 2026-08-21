"""
FocusDNA AI — Personalized User Baseline Engine (Phase 11)
Computes robust behavioral baseline statistics per user and blends global predictions
with personalized offsets based on minimum session sample thresholds.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd

class PersonalizedBaselineEngine:
    def __init__(self, min_sessions_threshold: int = 10, full_sessions_threshold: int = 30):
        self.min_sessions_threshold = min_sessions_threshold
        self.full_sessions_threshold = full_sessions_threshold

    def compute_user_baseline(self, user_sessions_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes robust median statistics for a user from their session history.
        """
        sample_count = len(user_sessions_history)
        if sample_count == 0:
            return {
                "sample_count": 0,
                "personalization_status": "insufficient_data",
                "median_duration_minutes": 25.0,
                "median_switch_freq": 4.0,
                "median_distraction_ratio": 0.1,
                "median_idle_ratio": 0.05
            }

        df_hist = pd.DataFrame(user_sessions_history)
        durations = df_hist["duration"].astype(float) if "duration" in df_hist.columns else pd.Series([25.0])
        distractions = df_hist["distraction_count"].astype(float) if "distraction_count" in df_hist.columns else pd.Series([0.0])

        status = "insufficient_data"
        if sample_count >= self.full_sessions_threshold:
            status = "fully_personalized"
        elif sample_count >= self.min_sessions_threshold:
            status = "hybrid_adapted"
        else:
            status = "learning_mode"

        return {
            "sample_count": sample_count,
            "personalization_status": status,
            "median_duration_minutes": float(np.median(durations)),
            "median_distraction_count": float(np.median(distractions)),
            "min_threshold": self.min_sessions_threshold,
            "full_threshold": self.full_sessions_threshold
        }

    def adjust_prediction(
        self,
        global_prob: float,
        current_features: Dict[str, Any],
        user_baseline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Blends global prediction with user baseline adjustments safely.
        """
        status = user_baseline.get("personalization_status", "insufficient_data")
        sample_count = user_baseline.get("sample_count", 0)

        if status == "insufficient_data" or sample_count < self.min_sessions_threshold:
            return {
                "final_probability": round(global_prob, 3),
                "personalization_applied": False,
                "personalization_status": f"Learning from {sample_count}/{self.min_sessions_threshold} labeled sessions",
                "user_baseline": user_baseline
            }

        # Calculate deviation from user's personal norm
        cur_switches = float(current_features.get("context_switch_frequency", 4.0))
        base_switches = float(user_baseline.get("median_switch_freq", 4.0))

        # Personal offset adjustment (-0.15 to +0.15)
        offset = 0.0
        if cur_switches > base_switches * 1.5:
            offset += 0.08
        elif cur_switches < base_switches * 0.7:
            offset -= 0.05

        weight = 0.3 if status == "hybrid_adapted" else 0.5
        adjusted_prob = max(0.0, min(1.0, global_prob + (offset * weight)))

        return {
            "final_probability": round(adjusted_prob, 3),
            "personalization_applied": True,
            "personalization_status": f"Personalized ({status}, {sample_count} sessions)",
            "user_baseline": user_baseline
        }

personalized_engine = PersonalizedBaselineEngine()
