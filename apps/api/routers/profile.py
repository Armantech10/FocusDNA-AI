from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from core.auth import get_current_user, AuthenticatedUser
from services.profile_service import profile_service
from routers.sessions import user_sessions_store
from routers.events import user_events_db

router = APIRouter(prefix="/api", tags=["Profile & Privacy Engine"])

user_profiles_db = {}
user_privacy_db = {}

class OnboardingRequest(BaseModel):
    display_name: str
    timezone: str = "UTC"
    tracking_consent: bool = True

class PrivacySettingsUpdate(BaseModel):
    is_tracking_paused: Optional[bool] = None
    collect_app_names: Optional[bool] = None
    collect_web_domains: Optional[bool] = None
    collect_typing_speed: Optional[bool] = None
    auto_purge_days: Optional[int] = None

@router.get("/profile")
def get_user_profile(user: AuthenticatedUser = Depends(get_current_user)):
    profile = user_profiles_db.get(user.user_id, {
        "user_id": user.user_id,
        "email": user.email,
        "display_name": "New User",
        "timezone": "UTC",
        "onboarding_completed": False
    })
    
    privacy = user_privacy_db.get(user.user_id, {
        "user_id": user.user_id,
        "is_tracking_paused": False,
        "collect_app_names": True,
        "collect_web_domains": True,
        "collect_typing_speed": True,
        "auto_purge_days": 90
    })

    return {
        "profile": profile,
        "privacy_settings": privacy
    }

@router.get("/profile/focusdna")
def get_focusdna_profile(user: AuthenticatedUser = Depends(get_current_user)):
    sessions = user_sessions_store.get(user.user_id, [])
    events = user_events_db.get(user.user_id, [])
    return profile_service.calculate_user_profile(sessions, events)

@router.get("/privacy/export")
def export_user_data(user: AuthenticatedUser = Depends(get_current_user)):
    """
    [User Privacy Right] Export My Data.
    Generates downloadable JSON payload of all stored user sessions and activity events.
    """
    sessions = user_sessions_store.get(user.user_id, [])
    events = user_events_db.get(user.user_id, [])
    profile = user_profiles_db.get(user.user_id, {})
    privacy = user_privacy_db.get(user.user_id, {})

    export_payload = {
        "export_metadata": {
            "user_id": user.user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "format": "FocusDNA Privacy Export v1.0"
        },
        "profile": profile,
        "privacy_settings": privacy,
        "focus_sessions_count": len(sessions),
        "focus_sessions": sessions,
        "activity_events_count": len(events),
        "activity_events": events
    }

    return JSONResponse(
        content=export_payload,
        headers={
            "Content-Disposition": f"attachment; filename=focusdna_user_export_{user.user_id[:8]}.json"
        }
    )

@router.post("/onboarding")
def complete_onboarding(
    data: OnboardingRequest, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    user_profiles_db[user.user_id] = {
        "user_id": user.user_id,
        "email": user.email,
        "display_name": data.display_name,
        "timezone": data.timezone,
        "onboarding_completed": True
    }
    
    user_privacy_db[user.user_id] = {
        "user_id": user.user_id,
        "is_tracking_paused": not data.tracking_consent,
        "collect_app_names": True,
        "collect_web_domains": True,
        "collect_typing_speed": True,
        "auto_purge_days": 90
    }

    return {
        "status": "success",
        "message": "Onboarding completed successfully.",
        "profile": user_profiles_db[user.user_id]
    }

@router.put("/privacy")
def update_privacy_controls(
    update: PrivacySettingsUpdate, 
    user: AuthenticatedUser = Depends(get_current_user)
):
    current = user_privacy_db.get(user.user_id, {
        "user_id": user.user_id,
        "is_tracking_paused": False,
        "collect_app_names": True,
        "collect_web_domains": True,
        "collect_typing_speed": True,
        "auto_purge_days": 90
    })

    for key, val in update.model_dump(exclude_none=True).items():
        current[key] = val

    user_privacy_db[user.user_id] = current

    return {
        "status": "updated",
        "privacy_settings": current
    }

@router.post("/privacy/revoke")
def revoke_tracking_consent(user: AuthenticatedUser = Depends(get_current_user)):
    """
    [User Privacy Right] Revoke Tracking Permission.
    Pauses tracking, updates consent state, and logs revocation.
    """
    user_privacy_db[user.user_id] = {
        "user_id": user.user_id,
        "is_tracking_paused": True,
        "collect_app_names": False,
        "collect_web_domains": False,
        "collect_typing_speed": False,
        "auto_purge_days": 90
    }
    return {
        "status": "consent_revoked",
        "user_id": user.user_id,
        "message": "Telemetry tracking consent revoked. Active tracking paused."
    }

@router.post("/privacy/purge")
def purge_user_data(user: AuthenticatedUser = Depends(get_current_user)):
    """
    [User Privacy Right] Delete My Data.
    Permanently deletes all focus sessions and activity events owned by user.
    """
    user_events_db[user.user_id] = []
    user_sessions_store[user.user_id] = []
    return {
        "status": "data_purged",
        "user_id": user.user_id,
        "message": f"Successfully deleted all activity events and sessions for user {user.user_id}."
    }
