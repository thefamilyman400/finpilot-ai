"""
API endpoints for AI-powered Recommendations
Handles recommendation generation, management, and actions
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.recommendation import RecommendationType, RecommendationStatus
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationResponse,
    RecommendationListResponse,
    RecommendationSummary,
    AcceptRecommendationRequest,
    RejectRecommendationRequest,
    CompleteRecommendationRequest,
    GenerateRecommendationsRequest,
    GenerateRecommendationsResponse,
)
from app.services.recommendation_service import recommendation_service


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/generate", response_model=GenerateRecommendationsResponse)
async def generate_recommendations(
    request: Optional[GenerateRecommendationsRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate AI-powered financial recommendations
    
    - Analyzes user's financial data
    - Generates personalized recommendations
    - Can focus on specific areas if requested
    """
    try:
        if request is None:
            request = GenerateRecommendationsRequest(
                focus_areas=None,
                max_recommendations=5,
                include_context=True
            )
        
        recommendations = await recommendation_service.generate_recommendations(
            db=db,
            user_id=str(current_user.id),
            focus_areas=request.focus_areas,
            max_recommendations=request.max_recommendations
        )
        
        # Get financial context if requested
        context_used = None
        if request.include_context:
            from app.services.ai_service import ai_service
            context_used = await ai_service.build_financial_context(db, str(current_user.id))
        
        return GenerateRecommendationsResponse(
            recommendations=[RecommendationResponse.model_validate(rec) for rec in recommendations],
            generation_summary=f"Generated {len(recommendations)} personalized recommendations based on your financial data.",
            total_generated=len(recommendations),
            context_used=context_used
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )


@router.get("", response_model=List[RecommendationResponse])
async def list_recommendations(
    status_filter: Optional[RecommendationStatus] = Query(None, alias="status"),
    type_filter: Optional[RecommendationType] = Query(None, alias="type"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List recommendations for the current user
    
    - Returns list of recommendations
    - Can filter by status and type
    - Ordered by priority and creation date
    """
    recommendations = await recommendation_service.get_user_recommendations(
        db=db,
        user_id=str(current_user.id),
        status=status_filter,
        type=type_filter,
        skip=skip,
        limit=limit
    )
    
    return recommendations


@router.get("/summary", response_model=RecommendationSummary)
async def get_recommendations_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics for user's recommendations
    
    - Total counts by status
    - Breakdown by type and priority
    - Total estimated savings
    """
    summary = await recommendation_service.get_recommendation_summary(
        db=db,
        user_id=str(current_user.id)
    )
    
    return RecommendationSummary(**summary)


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific recommendation
    
    - Returns full recommendation details
    - Only accessible by recommendation owner
    - Marks as viewed if not already viewed
    """
    recommendation = await recommendation_service.get_recommendation(
        db=db,
        recommendation_id=str(recommendation_id),
        user_id=str(current_user.id)
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Mark as viewed
    recommendation.mark_viewed()
    await db.commit()
    await db.refresh(recommendation)
    
    return RecommendationResponse.model_validate(recommendation)


@router.put("/{recommendation_id}", response_model=RecommendationResponse)
async def update_recommendation(
    recommendation_id: UUID,
    recommendation_update: RecommendationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a recommendation
    
    - Can update priority, status, notes, or active status
    - Only accessible by recommendation owner
    """
    update_data = recommendation_update.model_dump(exclude_unset=True)
    
    recommendation = await recommendation_service.update_recommendation(
        db=db,
        recommendation_id=str(recommendation_id),
        user_id=str(current_user.id),
        update_data=update_data
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return RecommendationResponse.model_validate(recommendation)


@router.post("/{recommendation_id}/accept", response_model=RecommendationResponse)
async def accept_recommendation(
    recommendation_id: UUID,
    request: Optional[AcceptRecommendationRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Accept a recommendation
    
    - Changes status to ACCEPTED
    - Records acceptance timestamp
    - Can include notes
    """
    notes = request.notes if request else None
    recommendation = await recommendation_service.accept_recommendation(
        db=db,
        recommendation_id=str(recommendation_id),
        user_id=str(current_user.id),
        notes=notes
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return RecommendationResponse.model_validate(recommendation)


@router.post("/{recommendation_id}/reject", response_model=RecommendationResponse)
async def reject_recommendation(
    recommendation_id: UUID,
    request: Optional[RejectRecommendationRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a recommendation
    
    - Changes status to REJECTED
    - Records rejection timestamp
    - Can include reason/notes
    """
    notes = None
    if request:
        notes = request.notes
        if hasattr(request, 'reason') and request.reason:
            notes = f"Reason: {request.reason}\n{notes}" if notes else f"Reason: {request.reason}"
    
    recommendation = await recommendation_service.reject_recommendation(
        db=db,
        recommendation_id=str(recommendation_id),
        user_id=str(current_user.id),
        notes=notes
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return RecommendationResponse.model_validate(recommendation)


@router.post("/{recommendation_id}/complete", response_model=RecommendationResponse)
async def complete_recommendation(
    recommendation_id: UUID,
    request: Optional[CompleteRecommendationRequest] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark recommendation as completed
    
    - Changes status to COMPLETED
    - Records completion timestamp
    - Can include actual results and notes
    """
    notes = None
    if request:
        notes = request.notes
        if hasattr(request, 'actual_savings') and request.actual_savings:
            savings_note = f"Actual savings: ${request.actual_savings:.2f}"
            notes = f"{savings_note}\n{notes}" if notes else savings_note
        
        if hasattr(request, 'actual_time_taken') and request.actual_time_taken:
            time_note = f"Time taken: {request.actual_time_taken}"
            notes = f"{notes}\n{time_note}" if notes else time_note
    
    recommendation = await recommendation_service.complete_recommendation(
        db=db,
        recommendation_id=str(recommendation_id),
        user_id=str(current_user.id),
        notes=notes
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return RecommendationResponse.model_validate(recommendation)


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    recommendation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a recommendation
    
    - Permanently deletes the recommendation
    - Only accessible by recommendation owner
    """
    recommendation = await recommendation_service.get_recommendation(
        db=db,
        recommendation_id=str(recommendation_id),
        user_id=str(current_user.id)
    )
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    await db.delete(recommendation)
    await db.commit()
    
    return None


# Made with Bob