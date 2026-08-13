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

@router.post("/finish")
def finish_session(
    data: SessionActionRequest, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Finishes focus session, calculates duration, status statistics, and Heuristic Focus Score.
    """
    sessions = user_sessions_store.get(user.user_id, [])
    session = next((s for s in sessions if s["id"] == data.session_id), None)
    
    if not session:
        raise HTTPException(status_code=404, detail="Focus session not found.")

    now_str = datetime.utcnow().isoformat()
    session["status"] = "completed"
    session["completed"] = True
    session["end_time"] = now_str
    session["distraction_count"] = data.distraction_count
    
    actual_mins = data.actual_duration_minutes if data.actual_duration_minutes is not None else session["planned_duration"]
    session["duration"] = actual_mins

    # Calculate Heuristic Focus Score
    heuristic_score = calculate_heuristic_focus_score(
        planned_minutes=session["planned_duration"],
        actual_minutes=actual_mins,
        distraction_count=data.distraction_count,
        status_state="completed"
    )
    session["heuristic_score"] = heuristic_score

    return {
        "status": "finished",
        "session": session,
        "statistics": {
            "planned_duration_minutes": session["planned_duration"],
            "actual_duration_minutes": actual_mins,
            "distraction_count": data.distraction_count,
            "heuristic_focus_score": heuristic_score
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
