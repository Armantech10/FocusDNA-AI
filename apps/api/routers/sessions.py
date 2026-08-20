from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from core.auth import get_current_user, AuthenticatedUser

router = APIRouter(prefix="/api/sessions", tags=["Focus Session Engine"])

# In-memory user-isolated sessions store for Phase 4 API verification (backed by Supabase PG in prod)
user_sessions_store: Dict[str, List[Dict[str, Any]]] = {}

class StartSessionRequest(BaseModel):
    session_name: str = "Deep Work Session"
    planned_duration_minutes: int = Field(default=25, ge=1, le=180)

class SessionActionRequest(BaseModel):
    session_id: str
    distraction_count: int = Field(default=0, ge=0)
    actual_duration_minutes: Optional[int] = None

def calculate_heuristic_focus_score(
    planned_minutes: int, 
    actual_minutes: int, 
    distraction_count: int, 
    status_state: str
) -> Dict[str, Any]:
    """
    Transparent Rule-Based Heuristic Focus Score Scorer.
    Explicitly labeled as 'Heuristic Focus Score' (NOT AI Prediction).
    """
    if status_state == "canceled":
        return {
            "score_value": 30.0,
            "label": "Canceled Session",
            "attribution": "Heuristic Focus Score",
            "explanation": "[Heuristic Focus Score] Session was canceled before completion target."
        }

    base_score = 100.0
    
    # Duration ratio penalty / bonus
    completion_ratio = min(1.0, actual_minutes / max(1, planned_minutes))
    ratio_penalty = (1.0 - completion_ratio) * 40.0
    
    # Distraction count penalty
    distraction_penalty = min(40.0, distraction_count * 8.0)
    
    final_score = max(0.0, min(100.0, base_score - ratio_penalty - distraction_penalty))
    
    return {
        "score_value": round(final_score, 1),
        "completion_ratio": round(completion_ratio * 100, 1),
        "attribution": "Heuristic Focus Score",
        "explanation": f"[Heuristic Focus Score] Evaluated from {round(completion_ratio*100)}% time completion and {distraction_count} distractions."
    }

@router.post("/start", status_code=status.HTTP_201_CREATED)
def start_session(
    data: StartSessionRequest, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Starts new focus session associated with user.
    """
    if user.user_id not in user_sessions_store:
        user_sessions_store[user.user_id] = []

    session_id = f"session_{user.user_id}_{len(user_sessions_store[user.user_id]) + 1}"
    now_str = datetime.utcnow().isoformat()

    new_session = {
        "id": session_id,
        "user_id": user.user_id,
        "session_name": data.session_name,
        "planned_duration": data.planned_duration_minutes,
        "duration": 0,
        "status": "active",
        "completed": False,
        "start_time": now_str,
        "end_time": None,
        "distraction_count": 0,
        "created_at": now_str
    }
    user_sessions_store[user.user_id].append(new_session)

    return {
        "status": "started",
        "session": new_session
    }

@router.post("/pause")
def pause_session(
    data: SessionActionRequest, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Pauses active focus session.
    """
    sessions = user_sessions_store.get(user.user_id, [])
    session = next((s for s in sessions if s["id"] == data.session_id), None)
    
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found.")

    session["status"] = "paused"
    session["distraction_count"] = data.distraction_count
    if data.actual_duration_minutes is not None:
        session["duration"] = data.actual_duration_minutes

    return {"status": "paused", "session": session}

@router.post("/resume")
def resume_session(
    data: SessionActionRequest, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Resumes paused focus session.
    """
    sessions = user_sessions_store.get(user.user_id, [])
    session = next((s for s in sessions if s["id"] == data.session_id), None)
    
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found.")

    session["status"] = "active"

    return {"status": "resumed", "session": session}

from services.heuristics import BehavioralHeuristicScorer, FeatureAggregator
from services.ml_service import ml_service
from routers.events import user_events_db

@router.post("/finish")
def finish_session(
    data: SessionActionRequest, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Finishes focus session, calculates duration, evaluates real telemetry events,
    and runs Random Forest / Isolation Forest ML models on real feature vectors.
    """
    sessions = user_sessions_store.get(user.user_id, [])
    session = next((s for s in sessions if s["id"] == data.session_id), None)
    
    if not session:
        # Create session fallback record if started client-side
        session = {
            "id": data.session_id,
            "user_id": user.user_id,
            "session_name": "Focus Session",
            "planned_duration": data.actual_duration_minutes or 25,
            "duration": data.actual_duration_minutes or 25,
            "status": "completed",
            "completed": True,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": datetime.utcnow().isoformat(),
            "distraction_count": data.distraction_count,
            "created_at": datetime.utcnow().isoformat()
        }
        if user.user_id not in user_sessions_store:
            user_sessions_store[user.user_id] = []
        user_sessions_store[user.user_id].append(session)

    now_str = datetime.utcnow().isoformat()
    session["status"] = "completed"
    session["completed"] = True
    session["end_time"] = now_str
    
    actual_mins = data.actual_duration_minutes if data.actual_duration_minutes is not None else session["planned_duration"]
    session["duration"] = actual_mins

    # 1. Fetch real telemetry events matching this session or user's recent window
    all_user_events = user_events_db.get(user.user_id, [])
    session_events = [e for e in all_user_events if e.get("focus_session_id") == data.session_id]
    
    if not session_events:
        session_events = all_user_events[-20:]

    has_real_telemetry = len(session_events) > 0

    # 2. Evaluate real Heuristic Focus Score
    heuristic_eval = BehavioralHeuristicScorer.evaluate_focus_score(user.user_id, session_events)
    session["distraction_count"] = max(data.distraction_count, int(heuristic_eval["breakdown"].get("social_penalty", 0) / 5) + int(heuristic_eval["breakdown"].get("entertainment_penalty", 0) / 4))

    # 3. Extract 6-Feature ML Vector & Run ML Inference
    feature_agg = FeatureAggregator.aggregate_features(user.user_id, session_events)
    total_dur = max(1.0, float(feature_agg.get("session_duration", actual_mins * 60)) / 60.0)
    total_switches = float(feature_agg.get("total_switches", 0))
    soc_sec = float(feature_agg.get("social_media_duration", 0))
    ent_sec = float(feature_agg.get("entertainment_duration", 0))
    idle_sec = float(feature_agg.get("idle_seconds", 0))

    ml_features = {
        "switch_frequency_5m": round((total_switches / total_dur) * 5.0, 2),
        "social_media_ratio": round(soc_sec / max(1.0, total_dur * 60.0), 3),
        "entertainment_ratio": round(ent_sec / max(1.0, total_dur * 60.0), 3),
        "idle_ratio": round(idle_sec / max(1.0, total_dur * 60.0), 3),
        "session_elapsed_minutes": round(total_dur, 1),
        "time_of_day_hour": datetime.utcnow().hour
    }

    ml_prediction = ml_service.predict_production_ml(ml_features)
    anomaly_eval = ml_service.detect_anomaly({
        "entertainment_duration_minutes": round(ent_sec / 60.0, 2),
        "switch_frequency_5m": ml_features["switch_frequency_5m"],
        "idle_seconds": idle_sec
    })

    session["heuristic_score"] = {
        "score_value": heuristic_eval["score_value"],
        "attribution": "Heuristic Focus Score",
        "explanation": heuristic_eval["explanation"],
        "is_distracted": heuristic_eval["is_distracted"],
        "breakdown": heuristic_eval["breakdown"]
    }
    session["ml_prediction"] = ml_prediction
    session["anomaly_evaluation"] = anomaly_eval
    session["has_real_telemetry"] = has_real_telemetry

    return {
        "status": "finished",
        "session": session,
        "telemetry_evaluated": {
            "has_real_telemetry": has_real_telemetry,
            "event_count": len(session_events),
            "heuristic_score": heuristic_eval,
            "ml_feature_vector": ml_features,
            "ml_prediction": {
                **ml_prediction,
                "label_notice": "RandomForest Model (Synthetic Baseline Trained)"
            },
            "anomaly_detection": anomaly_eval
        }
    }

@router.post("/cancel")
def cancel_session(
    data: SessionActionRequest, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Cancels focus session before completion.
    """
    sessions = user_sessions_store.get(user.user_id, [])
    session = next((s for s in sessions if s["id"] == data.session_id), None)
    
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found.")

    session["status"] = "canceled"
    session["completed"] = False
    session["end_time"] = datetime.utcnow().isoformat()
    if data.actual_duration_minutes is not None:
        session["duration"] = data.actual_duration_minutes

    heuristic_score = calculate_heuristic_focus_score(
        planned_minutes=session["planned_duration"],
        actual_minutes=session["duration"],
        distraction_count=data.distraction_count,
        status_state="canceled"
    )
    session["heuristic_score"] = heuristic_score

    return {"status": "canceled", "session": session}

@router.get("/history")
def get_session_history(user: AuthenticatedUser = Depends(get_current_user)):
    """
    Retrieves user-isolated focus session history and statistics.
    """
    sessions = user_sessions_store.get(user.user_id, [])
    completed_count = sum(1 for s in sessions if s.get("completed"))
    total_minutes = sum(s.get("duration", 0) for s in sessions if s.get("completed"))

    return {
        "user_id": user.user_id,
        "total_sessions": len(sessions),
        "completed_count": completed_count,
        "total_focus_minutes": total_minutes,
        "sessions": sessions
    }
