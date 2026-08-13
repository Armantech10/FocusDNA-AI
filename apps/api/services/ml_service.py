import os
import joblib
import pandas as pd
from typing import Dict, Any, List
from ml.models.anomaly_detector import BehavioralAnomalyDetector

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../ml/models/attention_loss_model.joblib")
MODEL_VERSION = "v1.0.0-GradientBoostedTrees"

class PredictiveAttentionService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PredictiveAttentionService, cls).__new__(cls)
            cls._instance.artifact = None
            cls._instance.model = None
            cls._instance.model_version = MODEL_VERSION
            cls._instance.feature_names = [
                "switch_frequency_5m",
                "social_media_ratio",
                "entertainment_ratio",
                "idle_ratio",
                "session_elapsed_minutes",
                "time_of_day_hour"
            ]
            cls._instance.anomaly_detector = BehavioralAnomalyDetector()
            cls._instance._load_model_safe()
        return cls._instance

    def _load_model_safe(self):
        normalized_path = os.path.abspath(MODEL_PATH)
        if os.path.exists(normalized_path):
            try:
                self.artifact = joblib.load(normalized_path)
                self.model = self.artifact["model"]
                m_name = self.artifact.get("model_name", "GradientBoostedTrees")
                self.model_version = f"v1.0.0-{m_name.replace(' ', '')}"
                self.feature_names = self.artifact.get("feature_names", self.feature_names)
                print(f"[ML Service Singleton] Successfully loaded model artifact ({self.model_version}).")
            except Exception as e:
                print(f"[ML Service Warning] Model file unreadable ({e}). Initialized fallback mode.")
                self.model = None
        else:
            print("[ML Service Notice] Joblib model file not found. Initialized fallback mode.")
            self.model = None

    def predict_production_ml(self, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Production Inference Method.
        Inputs: Pydantic validated behavioral features dictionary.
        Outputs exact requested JSON schema:
        {
          "prediction": "distracted" | "focused",
          "probability": 0.82,
          "model_version": "v1.0.0-GradientBoostedTrees",
          "explanation_features": [...]
        }
        """
        df_input = pd.DataFrame([{
            "switch_frequency_5m": float(input_features.get("switch_frequency_5m", 0.0)),
            "social_media_ratio": float(input_features.get("social_media_ratio", 0.0)),
            "entertainment_ratio": float(input_features.get("entertainment_ratio", 0.0)),
            "idle_ratio": float(input_features.get("idle_ratio", 0.0)),
            "session_elapsed_minutes": float(input_features.get("session_elapsed_minutes", 0.0)),
            "time_of_day_hour": int(input_features.get("time_of_day_hour", 14))
        }])[self.feature_names]

        if self.model is not None:
            try:
                prob = float(self.model.predict_proba(df_input)[0][1])
            except Exception:
                prob = self._heuristic_fallback_prob(input_features)
        else:
            prob = self._heuristic_fallback_prob(input_features)

        prob = max(0.0, min(1.0, round(prob, 2)))
        prediction_label = "distracted" if prob >= 0.5 else "focused"

        drivers: List[str] = []
        switches = float(input_features.get("switch_frequency_5m", 0.0))
        soc_ratio = float(input_features.get("social_media_ratio", 0.0))
        ent_ratio = float(input_features.get("entertainment_ratio", 0.0))
        elapsed = float(input_features.get("session_elapsed_minutes", 0.0))

        if switches >= 6:
            drivers.append(f"High context switch frequency ({int(switches)} switches/5m)")
        if soc_ratio > 0.1:
            drivers.append(f"Social media ratio ({round(soc_ratio * 100)}% time)")
        if ent_ratio > 0.1:
            drivers.append(f"Entertainment domain ratio ({round(ent_ratio * 100)}% time)")
        if elapsed > 45:
            drivers.append(f"Prolonged session duration ({int(elapsed)} mins elapsed)")

        if not drivers:
            drivers.append("Optimal digital behavior parameters")

        return {
            "prediction": prediction_label,
            "probability": prob,
            "model_version": self.model_version,
            "explanation_features": drivers
        }

    def predict_attention_loss(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy prediction method compatibility alias for test suite.
        """
        res = self.predict_production_ml(features)
        return {
            "risk_probability": res["probability"],
            "risk_percentage": round(res["probability"] * 100, 1),
            "risk_level": "High Risk" if res["prediction"] == "distracted" else "Low Risk",
            "is_high_risk": res["prediction"] == "distracted",
            "model_name": res["model_version"],
            "attribution_label": f"ML Predictive Model ({res['model_version']})",
            "primary_drivers": res["explanation_features"],
            "explanation": f"[{res['model_version']}] Prediction: {res['prediction'].upper()} ({round(res['probability']*100)}% probability). Drivers: {', '.join(res['explanation_features'])}."
        }

    def _heuristic_fallback_prob(self, input_features: Dict[str, Any]) -> float:
        switches = float(input_features.get("switch_frequency_5m", 0.0))
        soc_ratio = float(input_features.get("social_media_ratio", 0.0))
        return min(0.95, (switches * 0.08) + (soc_ratio * 0.5))

    def detect_anomaly(self, features: Dict[str, Any]) -> Dict[str, Any]:
        return self.anomaly_detector.detect_anomaly(features)

ml_service = PredictiveAttentionService()
