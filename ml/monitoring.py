"""
FocusDNA AI — Production Model Monitoring Subsystem (Phase 16)
Tracks model prediction counts, probability distributions, feedback agreement rates, and latency.
"""

from typing import Dict, Any, List
from datetime import datetime

class ModelMonitoringSubsystem:
    def __init__(self):
        self.prediction_logs: List[Dict[str, Any]] = []

    def log_prediction(
        self,
        prediction_id: str,
        model_version: str,
        probability: float,
        prediction_label: str,
        latency_ms: float,
        is_anomaly: bool = False
    ):
        """
        Logs anonymized prediction metrics. Zero raw browsing content stored.
        """
        self.prediction_logs.append({
            "id": prediction_id,
            "model_version": model_version,
            "probability": round(probability, 3),
            "prediction": prediction_label,
            "latency_ms": round(latency_ms, 2),
            "is_anomaly": is_anomaly,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_monitoring_summary(self) -> Dict[str, Any]:
        """
        Calculates aggregate monitoring metrics for backend admin dashboard.
        """
        total = len(self.prediction_logs)
        if total == 0:
            return {
                "total_predictions": 0,
                "attention_loss_rate": 0.0,
                "anomaly_rate": 0.0,
                "avg_probability": 0.0,
                "avg_latency_ms": 0.0,
                "active_model_versions": {}
            }

        attention_loss_count = sum(1 for p in self.prediction_logs if p["prediction"] == "distracted")
        anomaly_count = sum(1 for p in self.prediction_logs if p["is_anomaly"])
        avg_prob = sum(p["probability"] for p in self.prediction_logs) / total
        avg_latency = sum(p["latency_ms"] for p in self.prediction_logs) / total

        versions = {}
        for p in self.prediction_logs:
            v = p["model_version"]
            versions[v] = versions.get(v, 0) + 1

        return {
            "total_predictions": total,
            "attention_loss_rate": round((attention_loss_count / total) * 100, 1),
            "anomaly_rate": round((anomaly_count / total) * 100, 1),
            "avg_probability": round(avg_prob, 3),
            "avg_latency_ms": round(avg_latency, 2),
            "active_model_versions": versions
        }

ml_monitor = ModelMonitoringSubsystem()
