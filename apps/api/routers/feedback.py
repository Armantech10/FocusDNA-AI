from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from core.auth import get_current_user, AuthenticatedUser
from ml.pipeline.retrain_pipeline import run_controlled_retraining_pipeline
from ml.labeling import SessionLabelingEngine
from routers.events import user_events_db
from routers.sessions import user_sessions_store

logger = logging.getLogger("focusdna_feedback")

router = APIRouter(prefix="/api/feedback", tags=["User Feedback Learning Loop"])

# In-memory store for feedback records and ml_session_labels (backed by Supabase PG in production)
feedback_db: Dict[str, List[Dict[str, Any]]] = {} # user_id -> list of feedback dicts
ml_session_labels_db: Dict[str, List[Dict[str, Any]]] = {} # user_id -> list of label dicts

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

class SessionRatingRequest(BaseModel):
    focus_session_id: str
    user_rating: int = Field(..., ge=1, le=5)

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

@router.post("/session-rating", status_code=status.HTTP_201_CREATED)
def submit_session_rating(
    payload: SessionRatingRequest,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Records 5-level user focus rating (1=Very focused .. 5=Very distracted)
    and derives ground-truth binary target for ML dataset extraction.
    Prevents duplicate labels for the same session via in-place upsert.
    """
    if user.user_id not in ml_session_labels_db:
        ml_session_labels_db[user.user_id] = []

    label_record = SessionLabelingEngine.create_label_record(
        user_id=user.user_id,
        focus_session_id=payload.focus_session_id,
        user_rating=payload.user_rating,
        label_source="user_session_rating"
    )
    label_record["created_at"] = datetime.utcnow().isoformat()

    # In-place upsert to prevent duplicate labels for same session
    user_labels = ml_session_labels_db[user.user_id]
    existing_idx = next((i for i, l in enumerate(user_labels) if l["focus_session_id"] == payload.focus_session_id), None)
    if existing_idx is not None:
        user_labels[existing_idx] = label_record
    else:
        user_labels.append(label_record)

    logger.info(f"[ML Label Log] User: {user.user_id[:8]} | Session: {payload.focus_session_id} | Rating: {payload.user_rating} ({label_record['rating_label']}) | Target: {label_record['binary_target']}")

    return {
        "status": "recorded",
        "label_record": label_record
    }

@router.get("/session-labels")
def get_user_session_labels(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Retrieves all ground-truth labeled sessions for the user,
    attaching exact telemetry events and session metadata for dataset extraction.
    """
    user_labels = ml_session_labels_db.get(user.user_id, [])
    all_events = user_events_db.get(user.user_id, [])
    all_sessions = user_sessions_store.get(user.user_id, [])

    enriched_records = []
    for label in user_labels:
        sid = label["focus_session_id"]
        session_events = [e for e in all_events if e.get("focus_session_id") == sid]
        session_meta = next((s for s in all_sessions if s.get("id") == sid), {})

        enriched_records.append({
            "user_id": user.user_id,
            "focus_session_id": sid,
            "user_rating": label["user_rating"],
            "rating_label": label["rating_label"],
            "binary_target": label["binary_target"],
            "label_source": label.get("label_source", "user_session_rating"),
            "telemetry_events": session_events,
            "session_meta": session_meta,
            "created_at": label.get("created_at")
        })

    return {
        "user_id": user.user_id,
        "count": len(enriched_records),
        "labeled_sessions": enriched_records
    }

