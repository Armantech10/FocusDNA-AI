"""
FocusDNA AI — Model Registry & Versioning Engine (Phase 7)
Manages versioned model artifacts, metadata registry, production pointer, and atomic rollback.
"""

import os
import json
import joblib
from datetime import datetime
from typing import Dict, Any, List, Optional

REGISTRY_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(REGISTRY_DIR, "models")
REGISTRY_FILE = os.path.join(MODELS_DIR, "registry.json")

class ModelRegistry:
    def __init__(self, registry_file: str = REGISTRY_FILE):
        self.registry_file = registry_file
        os.makedirs(MODELS_DIR, exist_ok=True)
        self._ensure_registry_exists()

    def _ensure_registry_exists(self):
        if not os.path.exists(self.registry_file):
            initial_registry = {
                "active_production_version": "v1.0.0-PrototypeBaseline",
                "models": {}
            }
            with open(self.registry_file, "w") as f:
                json.dump(initial_registry, f, indent=2)

    def _read_registry(self) -> Dict[str, Any]:
        self._ensure_registry_exists()
        try:
            with open(self.registry_file, "r") as f:
                return json.load(f)
        except Exception:
            return {"active_production_version": "v1.0.0-PrototypeBaseline", "models": {}}

    def _write_registry(self, data: Dict[str, Any]):
        with open(self.registry_file, "w") as f:
            json.dump(data, f, indent=2)

    def register_model(
        self,
        model_version: str,
        model_type: str,
        model_object: Any,
        calibrator_object: Any,
        metrics: Dict[str, Any],
        dataset_meta: Dict[str, Any],
        feature_schema_version: str = "1.0",
        make_production: bool = False
    ) -> Dict[str, Any]:
        """
        Serializes artifact and records model metadata in registry.json.
        """
        artifact_name = f"{model_version}.joblib"
        artifact_path = os.path.join(MODELS_DIR, artifact_name)

        artifact = {
            "model_version": model_version,
            "model_type": model_type,
            "model": model_object,
            "calibrator": calibrator_object,
            "metrics": metrics,
            "dataset_meta": dataset_meta,
            "feature_schema_version": feature_schema_version,
            "trained_at": datetime.utcnow().isoformat()
        }

        joblib.dump(artifact, artifact_path)

        reg_data = self._read_registry()
        reg_data["models"][model_version] = {
            "model_version": model_version,
            "model_type": model_type,
            "artifact_path": artifact_path,
            "feature_schema_version": feature_schema_version,
            "dataset_type": dataset_meta.get("dataset_type", "synthetic_baseline"),
            "real_labeled_sessions_count": dataset_meta.get("real_labeled_sessions_count", 0),
            "metrics": metrics,
            "trained_at": artifact["trained_at"],
            "is_production": make_production
        }

        if make_production:
            for mv in reg_data["models"]:
                reg_data["models"][mv]["is_production"] = (mv == model_version)
            reg_data["active_production_version"] = model_version

        self._write_registry(reg_data)
        return reg_data["models"][model_version]

    def get_production_model_info(self) -> Optional[Dict[str, Any]]:
        reg_data = self._read_registry()
        prod_ver = reg_data.get("active_production_version")
        if prod_ver and prod_ver in reg_data["models"]:
            return reg_data["models"][prod_ver]
        return None

    def load_production_artifact(self) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        """
        Loads currently designated production artifact.
        """
        info = self.get_production_model_info()
        if info and os.path.exists(info["artifact_path"]):
            try:
                artifact = joblib.load(info["artifact_path"])
                return artifact, info
            except Exception as e:
                print(f"[ModelRegistry Warning] Failed to load production artifact: {e}")

        # Fallback to attention_loss_model.joblib
        fallback_path = os.path.join(MODELS_DIR, "attention_loss_model.joblib")
        if os.path.exists(fallback_path):
            try:
                artifact = joblib.load(fallback_path)
                return artifact, {
                    "model_version": "v1.0.0-PrototypeBaseline",
                    "model_type": "GradientBoostedTrees",
                    "feature_schema_version": "1.0",
                    "dataset_type": "synthetic_baseline",
                    "is_production": True
                }
            except Exception:
                pass

        return None, None

    def promote_to_production(self, model_version: str) -> Dict[str, Any]:
        """
        Promotes specified model version to production.
        """
        reg_data = self._read_registry()
        if model_version not in reg_data["models"]:
            raise ValueError(f"Model version '{model_version}' not found in registry.")

        previous_prod = reg_data.get("active_production_version")
        reg_data["previous_production_version"] = previous_prod
        reg_data["active_production_version"] = model_version

        for mv in reg_data["models"]:
            reg_data["models"][mv]["is_production"] = (mv == model_version)

        self._write_registry(reg_data)
        return reg_data["models"][model_version]

    def rollback_production(self) -> Optional[Dict[str, Any]]:
        """
        Rolls back production pointer to previous version.
        """
        reg_data = self._read_registry()
        prev_ver = reg_data.get("previous_production_version")
        if prev_ver and prev_ver in reg_data["models"]:
            return self.promote_to_production(prev_ver)
        return None

model_registry = ModelRegistry()
