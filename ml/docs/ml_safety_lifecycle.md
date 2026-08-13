# FocusDNA AI — Machine Learning Safety & Reliability Lifecycle Document

This document outlines the architectural boundaries and safety principles governing FocusDNA's ML pipeline. To ensure production stability, prevent data poisoning, and avoid positive feedback loops, **the production ML model is NEVER automatically retrained upon receiving user feedback events**.

---

## 1. Lifecycle Stage Separation

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ 1. DATA         │  ──>  │ 2. TRAINING     │  ──>  │ 3. EVALUATION   │  ──>  │ 4. DEPLOYMENT   │
│    COLLECTION   │       │    (OFFLINE)    │       │    (GATEKEEPER) │       │    (RELEASE)    │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
  In-memory / PG           Isolated Batch            Holdout Benchmark         Serialized Joblib
  Telemetry Logs           Re-fitting                F1-Score Check            Model Swap
```

---

### Stage 1: Data Collection
- **Role**: Continuously ingests anonymized telemetry and user feedback events (`helpful`, `not_helpful`, `was_actually_focused`, `was_distracted`, `dont_remind_again`).
- **Safety Boundary**: Data collection is strictly read-and-append. Telemetry and feedback records are written to durable storage without triggering model mutation or side effects.

### Stage 2: Training (Offline Batch)
- **Role**: Scheduled offline execution (`ml/pipeline/retrain_pipeline.py`).
- **Safety Boundary**: Training occurs in an isolated sandbox environment using curated, sanitized datasets. Training never executes inside HTTP request handlers or on live main looper threads.

### Stage 3: Evaluation (Gatekeeper)
- **Role**: Benchmarks candidate model against the current active production baseline model on an independent holdout test dataset.
- **Safety Boundary**: Evaluation gates enforce strict regression checks:
  - Candidate model **F1-Score** must strictly exceed active baseline model F1-Score.
  - Candidate model **Accuracy** and **Recall** must not degrade by more than `1.0%`.
  - If candidate fails evaluation gates, candidate is rejected and discarded.

### Stage 4: Deployment (Controlled Release)
- **Role**: Replaces `attention_loss_model.joblib` artifact and reloads the singleton model service in FastAPI.
- **Safety Boundary**: Deployment requires atomic artifact swaps with roll-back capabilities.

---

## 2. Why Immediate Auto-Retraining is Prohibited

1. **Feedback Loop Vulnerability**: Automatic retraining on instant user clicks creates feedback loop degradation where biased user signals corrupt decision boundaries.
2. **Data Poisoning Vulnerability**: Unvalidated online learning is susceptible to adversarial or accidental spamming of `was_actually_focused` clicks.
3. **Production Latency & Instability**: Retraining tree models on live HTTP request loops blocks main server threads and introduces memory leaks.
