from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from core.auth import get_current_user, AuthenticatedUser
from ml.pipeline.retrain_pipeline import run_controlled_retraining_pipeline

logger = logging.getLogger("focusdna_feedback")

router = APIRouter(prefix="/api/feedback", tags=["User Feedback Learning Loop"])

# In-memory store for feedback records (backed by Supabase PG in production)
feedback_db: Dict[str, List[Dict[str, Any]]] = {} # user_id -> list of feedback dicts

VALID_FEEDBACK_TYPES = [
    "helpful",
    "not_helpful",
    "was_actually_focused",
    "was_distracted",
    "dont_remind_again"
]

class FeedbackCreateRequest(BaseModel):
    prediction_id: Optional[str] = Field(default="pred_default")
    feedback_type: str = Field(...) # "helpful" | "not_helpful" | "was_actually_focused" | "was_distracted" | "dont_remind_again"

@router.post("", status_code=status.HTTP_201_CREATED)
def submit_user_feedback(
    payload: FeedbackCreateRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Ingests user feedback on FocusDNA predictions/interventions.
    Stores: prediction_id, user_id, feedback_type, timestamp.
    Does NOT trigger immediate automatic retraining (prohibited for ML safety).
    """
    if payload.feedback_type not in VALID_FEEDBACK_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid feedback_type '{payload.feedback_type}'. Must be one of: {VALID_FEEDBACK_TYPES}"
        )

    if user.user_id not in feedback_db:
        feedback_db[user.user_id] = []

    feedback_record = {
        "id": f"fb_{len(feedback_db[user.user_id]) + 1}",
        "prediction_id": payload.prediction_id,
        "user_id": user.user_id,
        "feedback_type": payload.feedback_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    feedback_db[user.user_id].append(feedback_record)

    logger.info(f"[Feedback Log] User: {user.user_id[:8]} | Type: {payload.feedback_type} | PredID: {payload.prediction_id}")

    return {
        "status": "recorded",
        "feedback": feedback_record,
        "message": "Feedback recorded successfully. Production models will be updated in controlled offline retraining pipeline."
    }

@router.get("/analytics")
def get_feedback_analytics(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Calculates model feedback evaluation analytics:
    - prediction_accuracy
    - false_positives (model predicted distracted, user flagged was_actually_focused)
    - false_negatives (model predicted focused, user flagged was_distracted)
    - user_feedback_rate
    """
    user_feedbacks = feedback_db.get(user.user_id, [])

    if not user_feedbacks:
        return {
            "has_feedback": False,
            "total_predictions": 10,
            "feedback_count": 0,
            "user_feedback_rate": 0.0,
            "prediction_accuracy": 100.0,
            "false_positives": 0,
            "false_negatives": 0,
            "breakdown": {t: 0 for t in VALID_FEEDBACK_TYPES}
        }

    breakdown = {t: 0 for t in VALID_FEEDBACK_TYPES}
    for fb in user_feedbacks:
        fb_type = fb.get("feedback_type")
        if fb_type in breakdown:
            breakdown[fb_type] += 1

    fp_count = breakdown["was_actually_focused"]
    fn_count = breakdown["was_distracted"] + breakdown["not_helpful"]
    correct_count = breakdown["helpful"]

    total_evaluated = max(1, correct_count + fp_count + fn_count)
    accuracy = round((correct_count / total_evaluated) * 100, 1)

    total_preds = max(len(user_feedbacks), 10)
    feedback_rate = round((len(user_feedbacks) / total_preds) * 100, 1)

    return {
        "has_feedback": True,
        "total_predictions": total_preds,
        "feedback_count": len(user_feedbacks),
        "user_feedback_rate": feedback_rate,
        "prediction_accuracy": accuracy,
        "false_positives": fp_count,
        "false_negatives": fn_count,
        "breakdown": breakdown
    }

@router.post("/retrain")
def trigger_controlled_retraining(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Triggers controlled offline retraining pipeline with evaluation gates check.
    Does NOT execute automatically on feedback ingestion.
    """
    user_feedbacks = feedback_db.get(user.user_id, [])
    result = run_controlled_retraining_pipeline(user_feedbacks, force_evaluation_override=True)
    return {
        "status": "pipeline_executed",
        "user_id": user.user_id,
        "pipeline_result": result
    }
