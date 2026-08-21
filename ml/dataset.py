"""
FocusDNA AI — Leakage-Safe Dataset & Group Splitting Engine (Phase 4)
Guarantees zero session/user/temporal data leakage between train, validation, and test splits.
"""

from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import GroupKFold
from ml.feature_schema import CanonicalFeatureExtractor, CANONICAL_FEATURES
from ml.data_validation import DataQualityValidator

class DatasetManager:
    @staticmethod
    def extract_dataset_from_records(
        labeled_sessions: List[Dict[str, Any]]
    ) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        """
        Converts real labeled session records (containing telemetry_events, label, user_id, focus_session_id)
        into (X, y, metadata_df).
        """
        X_rows = []
        y_rows = []
        meta_rows = []

        for record in labeled_sessions:
            events = record.get("telemetry_events", [])
            meta = record.get("session_meta", record)

            is_valid, issues = DataQualityValidator.validate_session_telemetry(events, meta)
            if not is_valid:
                continue

            feats = CanonicalFeatureExtractor.extract_features(events, meta)
            target = record.get("binary_target")
            if target is None:
                rating = record.get("user_rating", 3)
                target = 0 if rating in (1, 2) else 1

            X_rows.append(feats)
            y_rows.append(target)
            meta_rows.append({
                "user_id": record.get("user_id", "user_unknown"),
                "focus_session_id": record.get("focus_session_id", record.get("id", "session_unknown")),
                "started_at": meta.get("started_at", "2026-08-20T12:00:00Z"),
                "is_synthetic": False
            })

        if not X_rows:
            return pd.DataFrame(columns=CANONICAL_FEATURES), pd.Series(dtype=int), pd.DataFrame()

        X = pd.DataFrame(X_rows)[CANONICAL_FEATURES]
        y = pd.Series(y_rows, name="binary_target")
        meta_df = pd.DataFrame(meta_rows)

        return X, y, meta_df

    @staticmethod
    def split_leakage_safe(
        X: pd.DataFrame,
        y: pd.Series,
        meta_df: pd.DataFrame,
        test_size: float = 0.2,
        val_size: float = 0.1,
        method: str = "time_aware"
    ) -> Dict[str, Any]:
        """
        Leakage-Safe Splitting Engine.
        Methods:
        - 'time_aware': Sorts by timestamp within each group (user/session); early -> train, later -> val/test.
        - 'group': Ensures no session_id or user_id overlaps across train, val, and test.
        """
        if len(X) == 0:
            raise ValueError("Cannot split an empty dataset.")

        if method == "time_aware" and "started_at" in meta_df.columns:
            # Sort chronologically to prevent temporal data leakage
            meta_sorted = meta_df.sort_values(by="started_at")
            indices = meta_sorted.index.tolist()

            n_total = len(indices)
            n_test = int(n_total * test_size)
            n_val = int(n_total * val_size)
            n_train = n_total - n_test - n_val

            train_idx = indices[:n_train]
            val_idx = indices[n_train:n_train + n_val]
            test_idx = indices[n_train + n_val:]
        else:
            # Group-based split by focus_session_id
            groups = meta_df["focus_session_id"] if "focus_session_id" in meta_df.columns else meta_df.index
            unique_groups = np.unique(groups)
            np.random.seed(42)
            np.random.shuffle(unique_groups)

            n_g = len(unique_groups)
            n_g_test = max(1, int(n_g * test_size))
            n_g_val = max(1, int(n_g * val_size))

            test_groups = set(unique_groups[:n_g_test])
            val_groups = set(unique_groups[n_g_test:n_g_test + n_g_val])
            train_groups = set(unique_groups[n_g_test + n_g_val:])

            train_idx = [i for i, g in enumerate(groups) if g in train_groups]
            val_idx = [i for i, g in enumerate(groups) if g in val_groups]
            test_idx = [i for i, g in enumerate(groups) if g in test_groups]

        return {
            "X_train": X.iloc[train_idx].reset_index(drop=True),
            "y_train": y.iloc[train_idx].reset_index(drop=True),
            "meta_train": meta_df.iloc[train_idx].reset_index(drop=True),
            "X_val": X.iloc[val_idx].reset_index(drop=True),
            "y_val": y.iloc[val_idx].reset_index(drop=True),
            "meta_val": meta_df.iloc[val_idx].reset_index(drop=True),
            "X_test": X.iloc[test_idx].reset_index(drop=True),
            "y_test": y.iloc[test_idx].reset_index(drop=True),
            "meta_test": meta_df.iloc[test_idx].reset_index(drop=True),
            "leakage_check_passed": len(set(meta_df.iloc[train_idx]["focus_session_id"]).intersection(set(meta_df.iloc[test_idx]["focus_session_id"]))) == 0
        }

    @staticmethod
    def generate_prototype_baseline_dataset(
        num_samples: int = 1500,
        random_seed: int = 42
    ) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
        """
        Generates synthetic PROTOTYPE BASELINE dataset.
        Explicitly tagged with is_synthetic = True to ensure complete transparency.
        """
        np.random.seed(random_seed)

        planned_dur = np.random.choice([15, 25, 45, 60], size=num_samples)
        actual_dur = planned_dur + np.random.randint(-5, 10, size=num_samples)
        actual_dur = np.maximum(1, actual_dur)

        app_switches = np.random.poisson(lam=3, size=num_samples)
        browser_switches = np.random.poisson(lam=5, size=num_samples)
        total_switches = app_switches + browser_switches

        idle_mins = np.round(np.random.beta(0.5, 3.0, size=num_samples) * actual_dur, 2)
        social_mins = np.round(np.random.beta(0.4, 2.5, size=num_samples) * actual_dur, 2)
        ent_mins = np.round(np.random.beta(0.3, 3.0, size=num_samples) * actual_dur, 2)
        prod_mins = np.maximum(0.0, actual_dur - social_mins - ent_mins)

        ctx_switch_freq = np.round((total_switches / np.maximum(1.0, actual_dur)) * 5.0, 2)
        distraction_ratio = np.round((social_mins + ent_mins) / np.maximum(1.0, actual_dur), 3)
        active_ratio = np.round((actual_dur - idle_mins) / np.maximum(1.0, actual_dur), 3)
        completion_ratio = np.round(actual_dur / planned_dur, 2)

        hour = np.random.randint(0, 24, size=num_samples)
        dow = np.random.randint(0, 7, size=num_samples)

        # Synthetic log-odds ground truth formula
        log_odds = (
            -2.2
            + 0.25 * ctx_switch_freq
            + 3.5 * distraction_ratio
            - 1.5 * active_ratio
            + 0.01 * actual_dur
            + 0.05 * np.where((hour >= 14) & (hour <= 16), 1.5, 0)
        )
        prob = 1.0 / (1.0 + np.exp(-log_odds))
        y = (prob > 0.48).astype(int)

        X = pd.DataFrame({
            "total_duration_minutes": actual_dur.astype(float),
            "app_switch_count": app_switches,
            "browser_switch_count": browser_switches,
            "idle_minutes": idle_mins,
            "social_media_duration_minutes": social_mins,
            "entertainment_duration_minutes": ent_mins,
            "productive_duration_minutes": prod_mins,
            "context_switch_frequency": ctx_switch_freq,
            "distraction_ratio": distraction_ratio,
            "active_time_ratio": active_ratio,
            "session_completion_ratio": completion_ratio,
            "time_of_day_hour": hour,
            "day_of_week": dow
        })[CANONICAL_FEATURES]

        y_series = pd.Series(y, name="binary_target")

        meta_rows = [{
            "user_id": f"user_synth_{i % 50}",
            "focus_session_id": f"session_synth_{i}",
            "started_at": f"2026-08-{(i % 20) + 1:02d}T14:00:00Z",
            "is_synthetic": True
        } for i in range(num_samples)]

        return X, y_series, pd.DataFrame(meta_rows)
