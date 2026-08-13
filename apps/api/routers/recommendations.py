from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from core.auth import get_current_user, AuthenticatedUser
from services.gemini_service import gemini_service

router = APIRouter(tags=["AI Recommendations Engine"])

class AIRecommendationRequest(BaseModel):
    average_focus_session: Optional[float] = Field(default=35.0, ge=0)
    common_distraction_period: Optional[str] = Field(default="2:00 PM – 4:00 PM")
    average_switches: Optional[float] = Field(default=3.5, ge=0)
    top_trigger: Optional[str] = Field(default="Social Media")
    recent_anomaly: Optional[bool] = Field(default=False)
    focus_trend: Optional[str] = Field(default="stable")

class AIRecommendationResponse(BaseModel):
    explanation: str
    recommendation: str
    suggested_intervention: str
    cached: bool = False
    source: str = "heuristic_fallback"

@router.post("/api/ai/recommendation", response_model=AIRecommendationResponse)
def get_ai_recommendation(
    data: Optional[AIRecommendationRequest] = None,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Generates personalized AI recommendations & suggested interventions using Gemini REST API or heuristic fallback.
    Input: Structured telemetry statistics (never raw private content).
    Includes rate limiting, 15-minute response caching, and graceful failure handling.
    """
    input_stats = data.model_dump() if data else {}
    result = gemini_service.generate_recommendation(user.user_id, input_stats)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=result["message"]
        )

    return AIRecommendationResponse(**result)

@router.post("/api/insights/recommendations")
def get_insights_recommendations_alias(
    data: Optional[AIRecommendationRequest] = None,
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Alias endpoint compatibility router for UI insights page.
    """
    input_stats = data.model_dump() if data else {}
    result = gemini_service.generate_recommendation(user.user_id, input_stats)

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=result["message"]
        )

    return {
        "status": "success",
        "recommendation": result
    }
