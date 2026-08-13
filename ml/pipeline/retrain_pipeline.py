import os
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from ml.data.dataset_generator import generate_behavioral_dataset

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models"))
ACTIVE_MODEL_PATH = os.path.join(MODEL_DIR, "attention_loss_model.joblib")

def run_controlled_retraining_pipeline(
    feedback_records: list = None,
    force_evaluation_override: bool = False
) -> Dict[str, Any]:
    """
    Controlled Retraining Pipeline.
    1. Ingests collected feedback dataset.
    2. Fits candidate model offline.
    3. Benchmarks candidate vs active baseline model on holdout set.
    4. Deploys candidate ONLY if evaluation gates pass.
    """
    print("[Controlled Retraining Pipeline] Initializing offline training sandbox...")
    X, y = generate_behavioral_dataset(num_samples=2000, random_seed=100)

    # Convert user feedback signals into additional training samples if present
    if feedback_records:
        print(f"[Controlled Retraining Pipeline] Integrating {len(feedback_records)} curated user feedback records...")
        for fb in feedback_records:
            fb_type = fb.get("feedback_type")
            if fb_type == "was_actually_focused":
                # Add confirmed focused sample (y=0)
                sample = pd.DataFrame([{
                    "switch_frequency_5m": 2.0, "social_media_ratio": 0.0,
                    "entertainment_ratio": 0.0, "idle_ratio": 0.05,
                    "session_elapsed_minutes": 20.0, "time_of_day_hour": 10
                }])
                X = pd.concat([X, sample], ignore_index=True)
                y = pd.concat([y, pd.Series([0])], ignore_index=True)
            elif fb_type == "was_distracted":
                # Add confirmed distracted sample (y=1)
                sample = pd.DataFrame([{
                    "switch_frequency_5m": 12.0, "social_media_ratio": 0.40,
                    "entertainment_ratio": 0.20, "idle_ratio": 0.10,
                    "session_elapsed_minutes": 55.0, "time_of_day_hour": 15
                }])
                X = pd.concat([X, sample], ignore_index=True)
                y = pd.concat([y, pd.Series([1])], ignore_index=True)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 1. Fit Candidate Model
    print("[Controlled Retraining Pipeline] Fitting Candidate Model (Gradient Boosted Trees v1.1)...")
    candidate_model = GradientBoostingClassifier(n_estimators=120, max_depth=5, random_state=42)
    candidate_model.fit(X_train, y_train)

    cand_y_pred = candidate_model.predict(X_test)
    cand_f1 = float(f1_score(y_test, cand_y_pred, zero_division=0))
    cand_acc = float(accuracy_score(y_test, cand_y_pred))

    # 2. Evaluate against Baseline Model
    baseline_f1 = 0.90 # Default baseline target
    if os.path.exists(ACTIVE_MODEL_PATH):
        try:
            active_artifact = joblib.load(ACTIVE_MODEL_PATH)
            baseline_f1 = float(active_artifact.get("f1_score", 0.90))
        except Exception:
            pass

    print(f" -> Candidate F1-Score: {cand_f1:.4f} | Baseline F1-Score: {baseline_f1:.4f}")

    # 3. Evaluation Gatekeeper Decision
    passed_gates = (cand_f1 >= baseline_f1) or force_evaluation_override

    if passed_gates:
        print("[Controlled Retraining Pipeline] 🏆 Candidate passed evaluation gates! Deploying artifact...")
        artifact = {
            "model_name": "Gradient Boosted Trees v1.1 (Retrained)",
            "model": candidate_model,
            "feature_names": list(X.columns),
            "accuracy": round(cand_acc, 4),
            "f1_score": round(cand_f1, 4),
            "retrained_with_feedback_count": len(feedback_records) if feedback_records else 0
        }
        joblib.dump(artifact, ACTIVE_MODEL_PATH)
        status_msg = "Successfully retrained and deployed candidate model artifact."
    else:
        print("[Controlled Retraining Pipeline] 🛑 Candidate failed evaluation gates. Deployment aborted.")
        status_msg = "Candidate failed evaluation metrics check. Retrained model discarded."

    return {
        "status": "deployed" if passed_gates else "rejected",
        "passed_evaluation_gates": passed_gates,
        "candidate_f1_score": round(cand_f1, 4),
        "baseline_f1_score": round(baseline_f1, 4),
        "candidate_accuracy": round(cand_acc, 4),
        "message": status_msg
    }

if __name__ == "__main__":
    run_controlled_retraining_pipeline()
