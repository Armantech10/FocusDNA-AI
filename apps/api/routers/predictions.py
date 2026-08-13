from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, ConfigDict
from core.auth import get_current_user, AuthenticatedUser
from services.ml_service import ml_service

logger = logging.getLogger("focusdna_ml")

router = APIRouter(tags=["Production ML Prediction API"])

class MLPredictRequest(BaseModel):
    switch_frequency_5m: float = Field(default=0.0, ge=0)
    social_media_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    entertainment_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    idle_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    session_elapsed_minutes: float = Field(default=0.0, ge=0)
    time_of_day_hour: int = Field(default=14, ge=0, le=23)

class MLPredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    prediction: str
    probability: float
    model_version: str
    explanation_features: List[str]

class AnomalyDetectionRequest(BaseModel):
    entertainment_duration_minutes: Optional[float] = Field(default=None, ge=0)
    switch_frequency_5m: Optional[float] = Field(default=None, ge=0)
    idle_seconds: Optional[float] = Field(default=None, ge=0)

@router.post("/api/ml/predict", response_model=MLPredictResponse)
def production_ml_predict(
    data: MLPredictRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Production ML Prediction Endpoint.
    Input: Behavioral features Pydantic validated.
    Output: Exact schema {"prediction": "distracted", "probability": 0.82, "model_version": "...", "explanation_features": [...]}
    """
    input_dict = data.model_dump()
    result = ml_service.predict_production_ml(input_dict)

    logger.info(
        f"[ML Inference Log] User: {user.user_id[:8]}... | "
        f"Prediction: {result['prediction']} | Prob: {result['probability']} | Model: {result['model_version']}"
    )

    return MLPredictResponse(**result)

@router.post("/api/predict/attention-loss")
def predict_attention_loss_legacy(
    data: Optional[MLPredictRequest] = None,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Legacy ML Endpoint compatibility alias.
    """
    input_dict = data.model_dump() if data else {}
    result = ml_service.predict_production_ml(input_dict)

    return {
        "status": "predicted",
        "prediction": {
            "risk_probability": result["probability"],
            "risk_percentage": round(result["probability"] * 100, 1),
            "risk_level": "High Risk" if result["prediction"] == "distracted" else "Low Risk",
            "is_high_risk": result["prediction"] == "distracted",
            "model_version": result["model_version"],
            "attribution_label": f"ML Predictive Model ({result['model_version']})",
            "primary_drivers": result["explanation_features"],
            "explanation": f"[{result['model_version']}] Prediction: {result['prediction'].upper()} ({round(result['probability']*100)}% probability). Drivers: {', '.join(result['explanation_features'])}."
        }
    }

@router.post("/api/predict/anomaly")
def detect_behavioral_anomaly(
    data: Optional[AnomalyDetectionRequest] = None,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Unsupervised Isolation Forest Anomaly Detection endpoint.
    """
    input_dict = data.model_dump(exclude_none=True) if data else {}
    anomaly_result = ml_service.detect_anomaly(input_dict)

    return {
        "status": "analyzed",
        "user_id": user.user_id,
        "anomaly": anomaly_result
    }
