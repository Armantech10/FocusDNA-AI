"""
FocusDNA AI — Production ML Service Engine (Phase 8, 11, 16, 19, 20)
Singleton inference service delivering canonical feature extraction, calibrated attention-loss prediction,
hybrid personalization, Isolation Forest anomaly scoring, and explainability drivers.
"""

import time
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

from ml.feature_schema import CanonicalFeatureExtractor, CANONICAL_FEATURES, FEATURE_SCHEMA_VERSION
from ml.model_registry import model_registry
from ml.personalization import personalized_engine
from ml.models.anomaly_detector import BehavioralAnomalyDetector
from ml.monitoring import ml_monitor

class ProductionMLService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProductionMLService, cls).__new__(cls)
            cls._instance.anomaly_detector = BehavioralAnomalyDetector()
            cls._instance.feature_schema_version = FEATURE_SCHEMA_VERSION
            cls._instance.reload_model()
        return cls._instance

    def reload_model(self):
        """
        Reloads production model artifact and calibrator from ModelRegistry.
        """
        self.artifact, self.info = model_registry.load_production_artifact()
        if self.artifact:
            self.model = self.artifact.get("model")
            self.calibrator = self.artifact.get("calibrator")
            self.model_version = self.artifact.get("model_version", "v1.0.0-PrototypeBaseline")
            self.dataset_type = self.artifact.get("dataset_meta", {}).get("dataset_type", "synthetic_baseline")
            self.real_labeled_count = self.artifact.get("dataset_meta", {}).get("real_labeled_sessions_count", 0)
        else:
            self.model = None
            self.calibrator = None
            self.model_version = "v1.0.0-PrototypeBaseline"
            self.dataset_type = "synthetic_baseline"
            self.real_labeled_count = 0

    def predict_production_ml(
        self,
        telemetry_events: List[Dict[str, Any]] = None,
        session_meta: Dict[str, Any] = None,
        user_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Canonical Production Inference Pipeline:
        Telemetry -> Canonical Features -> Model -> Calibration -> Personalization -> Anomaly -> Monitoring -> Output
        """
        t0 = time.time()
        telemetry_events = telemetry_events or []
        session_meta = session_meta or {}
        user_history = user_history or []

        # 1. Extract Canonical Feature Vector
        features = CanonicalFeatureExtractor.extract_features(telemetry_events, session_meta)
        df_features = CanonicalFeatureExtractor.to_dataframe(features)

        # 2. Model Inference & Probability Calibration
        raw_prob = 0.5
        if self.model is not None:
            try:
                if hasattr(self.model, "predict_proba"):
                    raw_prob = float(self.model.predict_proba(df_features)[0][1])
                else:
                    raw_prob = float(self.model.predict(df_features)[0])
            except Exception:
                raw_prob = self._heuristic_fallback_prob(features)
        else:
            raw_prob = self._heuristic_fallback_prob(features)

        if self.calibrator is not None and hasattr(self.calibrator, "predict_proba"):
            calibrated_prob = float(self.calibrator.predict_proba(np.array([raw_prob]))[0])
        else:
            calibrated_prob = raw_prob

        # 3. Hybrid Personalization
        user_baseline = personalized_engine.compute_user_baseline(user_history)
        pers_res = personalized_engine.adjust_prediction(calibrated_prob, features, user_baseline)
        final_prob = pers_res["final_probability"]

        prediction_label = "distracted" if final_prob >= 0.5 else "focused"

        # 4. Isolation Forest Anomaly Engine
        anomaly_res = self.anomaly_detector.detect_anomaly(features)

        # 5. Explainability Drivers
        top_factors = self._derive_explainability_drivers(features)

        latency_ms = round((time.time() - t0) * 1000, 2)
        prediction_id = f"pred_{int(time.time() * 1000)}"

        # 6. Log Anonymized Metrics for Production Monitoring
        ml_monitor.log_prediction(
            prediction_id=prediction_id,
            model_version=self.model_version,
            probability=final_prob,
            prediction_label=prediction_label,
            latency_ms=latency_ms,
            is_anomaly=anomaly_res.get("is_anomaly", False)
        )

        model_notice = (
            "Prototype Baseline Model (Synthetic Baseline Trained)"
            if self.dataset_type == "synthetic_baseline" or self.real_labeled_count < 50
            else f"Production Model ({self.real_labeled_count} Real Labeled Sessions)"
        )

        return {
            "prediction_id": prediction_id,
            "prediction": prediction_label,
            "probability": final_prob,
            "attention_loss_probability": final_prob,
            "confidence": round(abs(final_prob - 0.5) * 2.0, 2),
            "model_version": self.model_version,
            "feature_schema_version": self.feature_schema_version,
            "model_notice": model_notice,
            "dataset_type": self.dataset_type,
            "real_labeled_sessions_count": self.real_labeled_count,
            "personalization": pers_res,
            "anomaly_detection": anomaly_res,
            "explanation_features": top_factors,
            "top_explanatory_factors": top_factors,
            "inference_latency_ms": latency_ms,
            "canonical_features": features
        }

    def _derive_explainability_drivers(self, features: Dict[str, Any]) -> List[str]:
        drivers = []
        ctx_switches = float(features.get("context_switch_frequency", 0.0))
        dist_ratio = float(features.get("distraction_ratio", 0.0))
        idle_mins = float(features.get("idle_minutes", 0.0))
        dur_mins = float(features.get("total_duration_minutes", 0.0))

        if ctx_switches >= 6.0:
            drivers.append(f"Elevated context switch frequency ({ctx_switches} switches/5m)")
        if dist_ratio > 0.15:
            drivers.append(f"High distraction domain ratio ({round(dist_ratio * 100)}% session time)")
        if idle_mins > 5.0:
            drivers.append(f"Extended idle duration ({round(idle_mins, 1)} minutes)")
        if dur_mins > 45.0:
            drivers.append(f"Prolonged session duration ({round(dur_mins)} minutes elapsed)")

        if not drivers:
            drivers.append("Optimal digital behavior parameters")
        return drivers

    def _heuristic_fallback_prob(self, features: Dict[str, Any]) -> float:
        switches = float(features.get("context_switch_frequency", 0.0))
        dist_ratio = float(features.get("distraction_ratio", 0.0))
        return min(0.95, (switches * 0.08) + (dist_ratio * 0.6))

    def detect_anomaly(self, features: Dict[str, Any]) -> Dict[str, Any]:
        return self.anomaly_detector.detect_anomaly(features)

    def predict_attention_loss(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy compatibility alias.
        """
        res = self.predict_production_ml(session_meta={"planned_duration_minutes": features.get("session_elapsed_minutes", 25)})
        return {
            "risk_probability": res["attention_loss_probability"],
            "risk_percentage": round(res["attention_loss_probability"] * 100, 1),
            "risk_level": "High Risk" if res["prediction"] == "distracted" else "Low Risk",
            "is_high_risk": res["prediction"] == "distracted",
            "model_name": res["model_version"],
            "attribution_label": f"ML Predictive Model ({res['model_version']})",
            "primary_drivers": res["top_explanatory_factors"],
            "explanation": f"[{res['model_version']}] Prediction: {res['prediction'].upper()} ({round(res['attention_loss_probability']*100)}% probability). Drivers: {', '.join(res['top_explanatory_factors'])}."
        }

ml_service = ProductionMLService()
