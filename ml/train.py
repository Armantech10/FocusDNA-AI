"""
FocusDNA AI — Model Training & Pipeline Engine (Phase 5, 6, 13)
Trains baseline models (RandomForest, GradientBoosting, LogisticRegression, Majority),
evaluates metrics, fits probability calibration, and saves versioned artifact to registry.
"""

import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, brier_score_loss

from ml.dataset import DatasetManager
from ml.feature_schema import CANONICAL_FEATURES
from ml.calibration import ProbabilityCalibrator
from ml.model_registry import model_registry

def train_and_evaluate_pipeline(
    labeled_records: list = None,
    model_version: str = "v1.1.0-GradientBoostingCandidate",
    promote_if_passed: bool = False
) -> Dict[str, Any]:
    """
    Executes end-to-end model training, comparison, calibration, and registration pipeline.
    If labeled_records is empty/insufficient, utilizes synthetic prototype baseline dataset
    and tags artifact explicitly as 'synthetic_baseline'.
    """
    print(f"[ML Pipeline] Starting training run for version '{model_version}'...")

    dataset_type = "real_labeled"
    real_count = len(labeled_records) if labeled_records else 0

    if real_count >= 50:
        print(f"[ML Pipeline] Using {real_count} real labeled session records...")
        X, y, meta_df = DatasetManager.extract_dataset_from_records(labeled_records)
    else:
        print(f"[ML Pipeline] Insufficient real labeled sessions ({real_count}/50). Using Prototype Baseline Synthetic Dataset...")
        dataset_type = "synthetic_baseline"
        X, y, meta_df = DatasetManager.generate_prototype_baseline_dataset(num_samples=1600, random_seed=42)

    splits = DatasetManager.split_leakage_safe(X, y, meta_df, test_size=0.2, val_size=0.1, method="time_aware")
    X_train, y_train = splits["X_train"], splits["y_train"]
    X_val, y_val = splits["X_val"], splits["y_val"]
    X_test, y_test = splits["X_test"], splits["y_test"]

    candidate_models = {
        "MajorityBaseline": DummyClassifier(strategy="most_frequent"),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight="balanced"),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    }

    results = {}
    best_model_name = "GradientBoosting"
    best_f1 = -1.0

    for name, model in candidate_models.items():
        t0 = time.time()
        model.fit(X_train, y_train)
        fit_time = round((time.time() - t0) * 1000, 2)

        val_preds = model.predict(X_val)
        val_f1 = float(f1_score(y_val, val_preds, zero_division=0))

        if hasattr(model, "predict_proba"):
            val_probs = model.predict_proba(X_val)[:, 1]
            val_auc = float(roc_auc_score(y_val, val_probs))
        else:
            val_probs = val_preds
            val_auc = 0.5

        results[name] = {
            "model": model,
            "val_f1": round(val_f1, 4),
            "val_auc": round(val_auc, 4),
            "fit_time_ms": fit_time
        }

        if val_f1 > best_f1:
            best_f1 = val_f1
            best_model_name = name

    winning_model = results[best_model_name]["model"]
    print(f"[ML Pipeline] 🏆 Winning Candidate: {best_model_name} (Val F1: {best_f1:.4f})")

    # Fit Probability Calibrator on Validation Set
    calibrator = ProbabilityCalibrator()
    if hasattr(winning_model, "predict_proba"):
        raw_val_probs = winning_model.predict_proba(X_val)[:, 1]
        calibrator.fit(raw_val_probs, y_val.values)

    # Test Set Evaluation
    test_preds = winning_model.predict(X_test)
    if hasattr(winning_model, "predict_proba"):
        raw_test_probs = winning_model.predict_proba(X_test)[:, 1]
        cal_test_probs = calibrator.predict_proba(raw_test_probs)
        test_auc = float(roc_auc_score(y_test, raw_test_probs))
    else:
        raw_test_probs = test_preds.astype(float)
        cal_test_probs = raw_test_probs
        test_auc = 0.5

    acc = float(accuracy_score(y_test, test_preds))
    prec = float(precision_score(y_test, test_preds, zero_division=0))
    rec = float(recall_score(y_test, test_preds, zero_division=0))
    f1 = float(f1_score(y_test, test_preds, zero_division=0))
    brier = float(brier_score_loss(y_test, cal_test_probs))

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(test_auc, 4),
        "brier_score": round(brier, 4),
        "winning_model_name": best_model_name,
        "all_candidates": {k: {"val_f1": v["val_f1"], "val_auc": v["val_auc"]} for k, v in results.items()}
    }

    dataset_meta = {
        "dataset_type": dataset_type,
        "real_labeled_sessions_count": real_count,
        "total_samples": len(X),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "leakage_check_passed": splits["leakage_check_passed"]
    }

    reg_entry = model_registry.register_model(
        model_version=model_version,
        model_type=best_model_name,
        model_object=winning_model,
        calibrator_object=calibrator,
        metrics=metrics,
        dataset_meta=dataset_meta,
        feature_schema_version="1.0",
        make_production=promote_if_passed
    )

    print(f"[ML Pipeline] Successfully registered model version '{model_version}'.")
    return reg_entry

if __name__ == "__main__":
    train_and_evaluate_pipeline(model_version="v1.0.0-PrototypeBaseline")
