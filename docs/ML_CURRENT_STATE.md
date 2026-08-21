# FocusDNA AI — ML Current State Audit (Phase 0)

**Date**: August 20, 2026  
**Auditor**: Antigravity ML Engineering Team  
**Scope**: Full codebase audit of `ml/`, `apps/api/services/ml_service.py`, `apps/api/routers/sessions.py`, `apps/api/routers/feedback.py`, and database schema.

---

## Executive Summary & Fact Sheet

| Inspection Criteria | Status / Audit Finding |
| :--- | :--- |
| **Active Production Model** | `GradientBoostingClassifier` serialized in `ml/models/attention_loss_model.joblib` |
| **Model Version** | `v1.0.0-GradientBoostedTrees` |
| **Input Feature Vector** | 6 features: `switch_frequency_5m`, `social_media_ratio`, `entertainment_ratio`, `idle_ratio`, `session_elapsed_minutes`, `time_of_day_hour` |
| **Target Variable** | Binary `attention_loss_risk` (0 = focused, 1 = distracted) |
| **Dataset Source** | **Synthetic Baseline** (1,200–1,600 samples generated programmatically via `dataset_generator.py`) |
| **Label Source** | Formulaic rule `(prob > 0.45)` based on synthetic Poisson/Beta feature distributions |
| **Evaluation Method** | Random 80/20 train/test split on synthetic samples |
| **Reported Metrics** | F1: ~0.9695 – 0.9776, Accuracy: ~95.0% – 96.25% (evaluated strictly on synthetic distribution) |
| **Data Leakage Check** | Synthetic rows are i.i.d.; however, lack of `user_id`/`session_id` group splitting presents potential time/user leakage when applied to real telemetry |
| **Production Loading** | Yes, loaded via singleton `PredictiveAttentionService` in `apps/api/services/ml_service.py` |
| **Isolation Forest Engine** | Active, trained on synthetic normal baseline (`normal_entertainment`, `normal_switches`, `normal_idle`) |
| **Canonical Feature Schema** | Missing unified feature schema module; feature definitions duplicated across 4 files |
| **Real User Labeling** | Basic feedback endpoint exists (`POST /api/feedback`), but no explicit `ml_session_labels` table/migration or user-facing 5-point session rating loop |
| **Probability Calibration** | Raw uncalibrated `predict_proba` output used as probability |
| **Personalization Baseline** | Static thresholds; no dynamic per-user median baseline or multi-tier sample count safeguard |

---

## Detailed Code Inventory

### 1. Model Artifact & Inference Service
- **Artifact Path**: [`ml/models/attention_loss_model.joblib`](file:///Users/arman/FocusDNA/ml/models/attention_loss_model.joblib)
- **Inference Module**: [`apps/api/services/ml_service.py`](file:///Users/arman/FocusDNA/apps/api/services/ml_service.py)
  - Loads `attention_loss_model.joblib` via `joblib.load()` on service startup.
  - Fallback logic: Uses linear heuristic calculation `min(0.95, switches * 0.08 + soc_ratio * 0.5)` if model file is missing or unreadable.
- **Anomaly Detection**: [`ml/models/anomaly_detector.py`](file:///Users/arman/FocusDNA/ml/models/anomaly_detector.py)
  - Uses `IsolationForest(n_estimators=100, contamination=0.08)`.

### 2. Training & Synthetic Generation
- **Data Generator**: [`ml/data/dataset_generator.py`](file:///Users/arman/FocusDNA/ml/data/dataset_generator.py)
  - Samples `switches` from `Poisson(lam=4)` and ratios from `Beta` distributions.
  - Calculates synthetic log-odds target.
- **Trainer & Comparator**:
  - [`ml/models/trainer.py`](file:///Users/arman/FocusDNA/ml/models/trainer.py): Trains `RandomForestClassifier`.
  - [`ml/models/comparator.py`](file:///Users/arman/FocusDNA/ml/models/comparator.py): Evaluates `RandomForest` vs `GradientBoostingClassifier` on synthetic split and saves winning model.
- **Retraining Pipeline**: [`ml/pipeline/retrain_pipeline.py`](file:///Users/arman/FocusDNA/ml/pipeline/retrain_pipeline.py)
  - Accepts user feedback records, appends synthetic samples matching feedback, fits `GradientBoostingClassifier(v1.1)`, checks candidate F1 score against baseline (F1 >= 0.90 gate), and overwrites artifact.

---

## Architectural Gaps & Required Upgrades

1. **Synthetic vs. Real Dataset Gap**: The active model was trained on synthetic data. Real telemetry from the Chrome extension and Focus Sessions must be captured, validated, and paired with real human session labels.
2. **Feature Synchronization**: Inference and training currently maintain independent feature dictionaries. A single canonical feature extractor module (`ml/feature_schema.py`) is required.
3. **Session Labeling System**: No standard 5-level user rating ("Very focused" to "Very distracted") or database table (`ml_session_labels`) exists to persist ground truth labels.
4. **Group-Based Leakage Protection**: Splitting must group by `user_id` and `focus_session_id`, with time-aware train/test splits for personal baselines.
5. **Model Registry & Card**: No structured model registry or standardized model card generation exists to track model versions, data policy, calibration metrics, and production status.
6. **Personalized Baseline Engine**: Needs dynamic user statistics (median context switch rate, idle ratio, distraction ratio) to transition seamlessly from global model to personalized prediction as user session count grows.
