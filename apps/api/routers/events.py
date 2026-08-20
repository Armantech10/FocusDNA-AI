from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from core.auth import get_current_user, AuthenticatedUser
from services.heuristics import BehavioralHeuristicScorer, FeatureAggregator

router = APIRouter(prefix="/api", tags=["Activity & Features"])

user_events_db = {}
user_scores_db = {}

class ActivityEventCreate(BaseModel):
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    application_name: Optional[str] = None
    website_domain: Optional[str] = None
    session_duration: int = Field(default=0, ge=0)
    app_switch_count: int = Field(default=0, ge=0)
    browser_switch_count: int = Field(default=0, ge=0)
    notification_count: int = Field(default=0, ge=0)
    idle_seconds: int = Field(default=0, ge=0)
    typing_activity_level: str = Field(default="low")
    device_type: str = Field(default="desktop")
    focus_session_id: Optional[str] = None

@router.post("/events", status_code=status.HTTP_201_CREATED)
def record_activity_event(
    event: ActivityEventCreate, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Records behavioral activity event associated exclusively with authenticated user.
    """
    if user.user_id not in user_events_db:
        user_events_db[user.user_id] = []

    record = event.model_dump()
    record["user_id"] = user.user_id
    record["id"] = f"event_{len(user_events_db[user.user_id]) + 1}"
    record["timestamp"] = record["timestamp"].isoformat() if isinstance(record["timestamp"], datetime) else record["timestamp"]
    
    user_events_db[user.user_id].append(record)

    return {
        "status": "recorded",
        "event_id": record["id"],
        "user_id": user.user_id,
        "total_user_events": len(user_events_db[user.user_id])
    }

@router.get("/events")
def get_user_events(
    focus_session_id: Optional[str] = None,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Retrieves events strictly owned by authenticated user (User Isolation).
    Optionally filter by focus_session_id.
    """
    events = user_events_db.get(user.user_id, [])
    if focus_session_id:
        events = [e for e in events if e.get("focus_session_id") == focus_session_id]
    return {
        "user_id": user.user_id,
        "count": len(events),
        "events": events
    }

@router.post("/focus/evaluate")
def evaluate_focus_score(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Aggregates recent activity event features and evaluates transparent Heuristic Focus Score with explainable rationale.
    """
    events = user_events_db.get(user.user_id, [])
    score_result = BehavioralHeuristicScorer.evaluate_focus_score(user.user_id, events[-20:])

    if user.user_id not in user_scores_db:
        user_scores_db[user.user_id] = []

    score_record = {
        "id": f"score_{len(user_scores_db[user.user_id]) + 1}",
        "user_id": user.user_id,
        "score_value": score_result["score_value"],
        "evaluation_type": "heuristic",
        "explanation": score_result["explanation"],
        "features": score_result["features"],
        "breakdown": score_result["breakdown"],
        "timestamp": datetime.utcnow().isoformat()
    }
    user_scores_db[user.user_id].append(score_record)

    return {
        "status": "evaluated",
        "score": score_record
    }
