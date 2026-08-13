import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.ensemble import IsolationForest

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
ANOMALY_MODEL_PATH = os.path.join(MODEL_DIR, "anomaly_model.joblib")

def train_isolation_forest() -> Dict[str, Any]:
    """
    Trains Isolation Forest anomaly detector to identify statistical behavioral outliers
    (e.g., entertainment domain usage spiking from normal 10m baseline to 90m).
    """
    np.random.seed(42)
    num_samples = 1000

    # Baseline normal user behavior (e.g. 5-15 mins entertainment, 2-6 switches/5m)
    normal_entertainment = np.random.gamma(shape=2.0, scale=5.0, size=num_samples)
    normal_switches = np.random.poisson(lam=4, size=num_samples)
    normal_idle = np.random.exponential(scale=30, size=num_samples)

    df_normal = pd.DataFrame({
        "entertainment_duration_minutes": np.round(normal_entertainment, 1),
        "switch_frequency_5m": normal_switches,
        "idle_seconds": np.round(normal_idle, 1)
    })

    print("[ML Anomaly Detector] Training Isolation Forest model...")
    model = IsolationForest(
        n_estimators=100,
        contamination=0.08,
        random_state=42
    )
    model.fit(df_normal)

    artifact = {
        "model": model,
        "feature_names": list(df_normal.columns),
        "baseline_means": df_normal.mean().to_dict(),
        "baseline_stds": df_normal.std().to_dict()
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(artifact, ANOMALY_MODEL_PATH)
    print(f"[ML Anomaly Detector] Anomaly model artifact saved to: {ANOMALY_MODEL_PATH}")
    return artifact

class BehavioralAnomalyDetector:
    def __init__(self):
        self.artifact = None
        self.model = None
        self.feature_names = ["entertainment_duration_minutes", "switch_frequency_5m", "idle_seconds"]
        self._load_model()

    def _load_model(self):
        normalized_path = os.path.abspath(ANOMALY_MODEL_PATH)
        if os.path.exists(normalized_path):
            try:
                self.artifact = joblib.load(normalized_path)
                self.model = self.artifact["model"]
                self.feature_names = self.artifact.get("feature_names", self.feature_names)
            except Exception as e:
                print(f"[ML Anomaly Detector Warning] Failed to load model: {e}")

    def detect_anomaly(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs Isolation Forest anomaly detection inference.
        """
        if self.model is None:
            self._load_model()

        ent_mins = float(features.get("entertainment_duration_minutes", features.get("entertainment_duration", 10.0)))
        switches = float(features.get("switch_frequency_5m", features.get("total_switches", 4)))
        idle = float(features.get("idle_seconds", 15.0))

        df_input = pd.DataFrame([{
            "entertainment_duration_minutes": ent_mins,
            "switch_frequency_5m": switches,
            "idle_seconds": idle
        }])[self.feature_names]

        if self.model:
            pred = int(self.model.predict(df_input)[0]) # -1 = anomaly, 1 = normal
            score = float(self.model.score_samples(df_input)[0]) # Lower score = higher anomaly
            is_anomaly = (pred == -1) or (ent_mins >= 45.0)
        else:
            is_anomaly = (ent_mins >= 45.0) or (switches >= 18)
            score = -0.65 if is_anomaly else 0.45

        reasons = []
        if ent_mins >= 45.0:
            reasons.append(f"Entertainment usage reached {round(ent_mins)} minutes (significantly above 10m baseline)")
        if switches >= 15:
            reasons.append(f"Extreme switch rate ({int(switches)} switches in window)")
        if idle >= 300:
            reasons.append(f"Extended idle duration ({int(idle)}s idle)")

        if not reasons:
            explanation = "[Isolation Forest Anomaly Engine] Behavioral patterns align with baseline user norms."
        else:
            explanation = f"[Isolation Forest Anomaly Engine] Behavioral Anomaly Signal Detected! {', '.join(reasons)}."

        return {
          "is_anomaly": is_anomaly,
          "anomaly_score": round(score, 3),
          "model_type": "IsolationForest",
          "explanation": explanation,
          "anomalous_features": reasons,
          "input_features": {
              "entertainment_duration_minutes": ent_mins,
              "switch_frequency_5m": switches,
              "idle_seconds": idle
          }
        }

if __name__ == "__main__":
    train_isolation_forest()
