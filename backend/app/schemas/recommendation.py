"""
Pydantic schemas for Recommendation model
Used for request/response validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from app.models.recommendation import (
    RecommendationType,
    RecommendationPriority,
    RecommendationStatus
)


# ============================================================================
# Recommendation Schemas
# ============================================================================

class RecommendationBase(BaseModel):
    """Base schema for Recommendation"""
    type: RecommendationType
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)


class RecommendationCreate(RecommendationBase):
    """Schema for creating a new recommendation"""
    rationale: Optional[str] = None
    estimated_savings: Optional[float] = Field(None, ge=0)
    estimated_time_to_implement: Optional[str] = None
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    action_items: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None
    conversation_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation"""
    priority: Optional[RecommendationPriority] = None
    status: Optional[RecommendationStatus] = None
    user_notes: Optional[str] = None
    is_active: Optional[bool] = None


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response"""
    id: UUID
    user_id: UUID
    status: RecommendationStatus
    rationale: Optional[str] = None
    estimated_savings: Optional[float] = None
    estimated_time_to_implement: Optional[str] = None
    confidence_score: Optional[float] = None
    action_items: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None
    ai_model: Optional[str] = None
    conversation_id: Optional[UUID] = None
    viewed_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    user_notes: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    is_pending: bool
    is_accepted: bool
    is_completed: bool
    is_expired: bool
    days_since_created: int
    priority_score: int
    
    model_config = ConfigDict(from_attributes=True)


class RecommendationListResponse(BaseModel):
    """Schema for paginated recommendation list"""
    recommendations: List[RecommendationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RecommendationSummary(BaseModel):
    """Schema for recommendation summary statistics"""
    total_recommendations: int
    pending_count: int
    accepted_count: int
    completed_count: int
    rejected_count: int
    total_estimated_savings: float
    by_type: Dict[str, int]
    by_priority: Dict[str, int]


# ============================================================================
# Action Schemas
# ============================================================================

class RecommendationActionRequest(BaseModel):
    """Schema for recommendation actions (accept/reject/complete)"""
    notes: Optional[str] = Field(None, description="User notes about the action")


class AcceptRecommendationRequest(RecommendationActionRequest):
    """Schema for accepting a recommendation"""
    pass


class RejectRecommendationRequest(RecommendationActionRequest):
    """Schema for rejecting a recommendation"""
    reason: Optional[str] = Field(None, description="Reason for rejection")


class CompleteRecommendationRequest(RecommendationActionRequest):
    """Schema for marking recommendation as completed"""
    actual_savings: Optional[float] = Field(None, ge=0, description="Actual savings achieved")
    actual_time_taken: Optional[str] = Field(None, description="Actual time taken to implement")


# ============================================================================
# Generation Schemas
# ============================================================================

class GenerateRecommendationsRequest(BaseModel):
    """Schema for requesting AI to generate recommendations"""
    focus_areas: Optional[List[RecommendationType]] = Field(
        None,
        description="Specific areas to focus on (optional)"
    )
    max_recommendations: int = Field(
        5,
        ge=1,
        le=20,
        description="Maximum number of recommendations to generate"
    )
    include_context: bool = Field(
        True,
        description="Include financial context in generation"
    )


class GenerateRecommendationsResponse(BaseModel):
    """Schema for recommendation generation response"""
    recommendations: List[RecommendationResponse]
    generation_summary: str
    total_generated: int
    context_used: Optional[Dict[str, Any]] = None


class RecommendationInsight(BaseModel):
    """Schema for insights about recommendations"""
    insight_type: str = Field(..., description="Type of insight")
    title: str
    description: str
    related_recommendations: List[UUID] = Field(default_factory=list)
    data: Optional[Dict[str, Any]] = None


class RecommendationImpactAnalysis(BaseModel):
    """Schema for analyzing recommendation impact"""
    recommendation_id: UUID
    potential_monthly_savings: Optional[float] = None
    potential_annual_savings: Optional[float] = None
    implementation_difficulty: str = Field(..., description="easy, medium, hard")
    time_to_see_results: str = Field(..., description="immediate, short-term, long-term")
    risk_level: str = Field(..., description="low, medium, high")
    dependencies: List[str] = Field(default_factory=list)


# ============================================================================
# Filter Schemas
# ============================================================================

class RecommendationFilters(BaseModel):
    """Schema for filtering recommendations"""
    type: Optional[RecommendationType] = None
    priority: Optional[RecommendationPriority] = None
    status: Optional[RecommendationStatus] = None
    is_active: Optional[bool] = None
    min_savings: Optional[float] = Field(None, ge=0)
    max_savings: Optional[float] = Field(None, ge=0)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    conversation_id: Optional[UUID] = None


# Made with Bob