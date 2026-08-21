"""
FocusDNA AI — Feature Drift Engine (Phase 17)
Calculates Population Stability Index (PSI) to detect feature distribution drift.
"""

from typing import Dict, Any, List
import numpy as np
import pandas as pd

class FeatureDriftDetector:
    @staticmethod
    def calculate_psi(reference: np.ndarray, current: np.ndarray, num_bins: int = 10) -> float:
        """
        Calculates Population Stability Index (PSI) between reference and current feature distributions.
        PSI < 0.1: No significant drift
        0.1 <= PSI < 0.25: Moderate drift (Retraining recommended)
        PSI >= 0.25: Significant drift (Retraining strongly recommended)
        """
        if len(reference) < 10 or len(current) < 10:
            return 0.0

        percentiles = np.linspace(0, 100, num_bins + 1)
        bins = np.percentile(reference, percentiles)
        bins[0] = -np.inf
        bins[-1] = np.inf

        ref_counts, _ = np.histogram(reference, bins=bins)
        curr_counts, _ = np.histogram(current, bins=bins)

        ref_pct = np.clip(ref_counts / len(reference), 1e-4, 1.0)
        curr_pct = np.clip(curr_counts / len(current), 1e-4, 1.0)

        psi = float(np.sum((curr_pct - ref_pct) * np.log(curr_pct / ref_pct)))
        return round(max(0.0, psi), 4)

    @staticmethod
    def evaluate_feature_drift(
        reference_df: pd.DataFrame,
        current_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Evaluates drift across key features.
        """
        if reference_df.empty or current_df.empty:
            return {
                "drift_detected": False,
                "max_psi": 0.0,
                "status": "Insufficient data for drift analysis",
                "feature_psi": {}
            }

        key_features = [
            "context_switch_frequency",
            "idle_minutes",
            "distraction_ratio",
            "browser_switch_count",
            "total_duration_minutes"
        ]

        feature_psi = {}
        max_psi = 0.0

        for feat in key_features:
            if feat in reference_df.columns and feat in current_df.columns:
                psi = FeatureDriftDetector.calculate_psi(
                    reference_df[feat].dropna().values,
                    current_df[feat].dropna().values
                )
                feature_psi[feat] = psi
                if psi > max_psi:
                    max_psi = psi

        drift_detected = max_psi >= 0.1
        status_msg = "Retraining recommended (Feature drift detected)" if drift_detected else "Feature distribution stable"

        return {
            "drift_detected": drift_detected,
            "max_psi": max_psi,
            "status": status_msg,
            "feature_psi": feature_psi
        }
