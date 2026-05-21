"""
Recommendation Service for AI-powered financial recommendations
Generates, manages, and tracks personalized financial recommendations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
import json

from openai import AsyncOpenAI

from app.models.recommendation import (
    Recommendation,
    RecommendationType,
    RecommendationPriority,
    RecommendationStatus
)
from app.models.user import User
from app.services.ai_service import ai_service
from config import settings


class RecommendationService:
    """
    Service for generating and managing AI-powered financial recommendations
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def create_recommendation(
        self,
        db: AsyncSession,
        user_id: str,
        recommendation_data: Dict[str, Any]
    ) -> Recommendation:
        """Create a new recommendation"""
        recommendation = Recommendation(
            user_id=user_id,
            **recommendation_data
        )
        db.add(recommendation)
        await db.commit()
        await db.refresh(recommendation)
        return recommendation
    
    async def get_recommendation(
        self,
        db: AsyncSession,
        recommendation_id: str,
        user_id: str
    ) -> Optional[Recommendation]:
        """Get a recommendation by ID"""
        result = await db.execute(
            select(Recommendation).where(
                Recommendation.id == recommendation_id,
                Recommendation.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_recommendations(
        self,
        db: AsyncSession,
        user_id: str,
        status: Optional[RecommendationStatus] = None,
        type: Optional[RecommendationType] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Recommendation]:
        """Get recommendations for a user with optional filters"""
        query = select(Recommendation).where(
            Recommendation.user_id == user_id,
            Recommendation.is_active == True
        )
        
        if status:
            query = query.where(Recommendation.status == status)
        if type:
            query = query.where(Recommendation.type == type)
        
        query = query.order_by(
            desc(Recommendation.priority),
            desc(Recommendation.created_at)
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def update_recommendation(
        self,
        db: AsyncSession,
        recommendation_id: str,
        user_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Recommendation]:
        """Update a recommendation"""
        recommendation = await self.get_recommendation(db, recommendation_id, user_id)
        if not recommendation:
            return None
        
        for key, value in update_data.items():
            if hasattr(recommendation, key):
                setattr(recommendation, key, value)
        
        await db.commit()
        await db.refresh(recommendation)
        return recommendation
    
    async def accept_recommendation(
        self,
        db: AsyncSession,
        recommendation_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> Optional[Recommendation]:
        """Accept a recommendation"""
        recommendation = await self.get_recommendation(db, recommendation_id, user_id)
        if not recommendation:
            return None
        
        recommendation.accept()
        if notes:
            recommendation.user_notes = notes
        
        await db.commit()
        await db.refresh(recommendation)
        return recommendation
    
    async def reject_recommendation(
        self,
        db: AsyncSession,
        recommendation_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> Optional[Recommendation]:
        """Reject a recommendation"""
        recommendation = await self.get_recommendation(db, recommendation_id, user_id)
        if not recommendation:
            return None
        
        recommendation.reject(notes)
        
        await db.commit()
        await db.refresh(recommendation)
        return recommendation
    
    async def complete_recommendation(
        self,
        db: AsyncSession,
        recommendation_id: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> Optional[Recommendation]:
        """Mark recommendation as completed"""
        recommendation = await self.get_recommendation(db, recommendation_id, user_id)
        if not recommendation:
            return None
        
        recommendation.complete(notes)
        
        await db.commit()
        await db.refresh(recommendation)
        return recommendation
    
    async def get_recommendation_summary(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """Get summary statistics for user's recommendations"""
        result = await db.execute(
            select(Recommendation).where(
                Recommendation.user_id == user_id,
                Recommendation.is_active == True
            )
        )
        recommendations = result.scalars().all()
        
        summary = {
            "total_recommendations": len(recommendations),
            "pending_count": sum(1 for r in recommendations if r.is_pending),
            "accepted_count": sum(1 for r in recommendations if r.is_accepted),
            "completed_count": sum(1 for r in recommendations if r.is_completed),
            "rejected_count": sum(1 for r in recommendations if r.status == RecommendationStatus.REJECTED),
            "total_estimated_savings": sum(r.estimated_savings or 0 for r in recommendations if r.is_pending or r.is_accepted),
            "by_type": {},
            "by_priority": {}
        }
        
        # Count by type
        for rec_type in RecommendationType:
            count = sum(1 for r in recommendations if r.type == rec_type)
            if count > 0:
                summary["by_type"][rec_type.value] = count
        
        # Count by priority
        for priority in RecommendationPriority:
            count = sum(1 for r in recommendations if r.priority == priority)
            if count > 0:
                summary["by_priority"][priority.value] = count
        
        return summary
    
    async def generate_recommendations(
        self,
        db: AsyncSession,
        user_id: str,
        focus_areas: Optional[List[RecommendationType]] = None,
        max_recommendations: int = 5
    ) -> List[Recommendation]:
        """
        Generate AI-powered recommendations based on user's financial data
        """
        # Get financial context
        financial_context = await ai_service.build_financial_context(db, user_id)
        
        # Build prompt for recommendation generation
        prompt = self._build_recommendation_prompt(financial_context, focus_areas, max_recommendations)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial advisor AI. Generate personalized financial recommendations in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse AI response
            recommendations_data = json.loads(response.choices[0].message.content)
            
            # Create recommendation objects
            created_recommendations = []
            for rec_data in recommendations_data.get("recommendations", [])[:max_recommendations]:
                recommendation = await self.create_recommendation(
                    db,
                    user_id,
                    {
                        "type": RecommendationType(rec_data.get("type", "other")),
                        "priority": RecommendationPriority(rec_data.get("priority", "medium")),
                        "title": rec_data.get("title"),
                        "description": rec_data.get("description"),
                        "rationale": rec_data.get("rationale"),
                        "estimated_savings": rec_data.get("estimated_savings"),
                        "estimated_time_to_implement": rec_data.get("estimated_time_to_implement"),
                        "confidence_score": rec_data.get("confidence_score", 0.7),
                        "action_items": rec_data.get("action_items", []),
                        "resources": rec_data.get("resources", []),
                        "context": financial_context,
                        "ai_model": self.model
                    }
                )
                created_recommendations.append(recommendation)
            
            return created_recommendations
            
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            raise
    
    def _build_recommendation_prompt(
        self,
        financial_context: Dict[str, Any],
        focus_areas: Optional[List[RecommendationType]],
        max_recommendations: int
    ) -> str:
        """Build prompt for AI recommendation generation"""
        prompt = f"""Based on the following financial context, generate {max_recommendations} personalized financial recommendations.

Financial Context:
{json.dumps(financial_context, indent=2)}

"""
        
        if focus_areas:
            areas = ", ".join([area.value for area in focus_areas])
            prompt += f"Focus on these areas: {areas}\n\n"
        
        prompt += """Generate recommendations in the following JSON format:
{
  "recommendations": [
    {
      "type": "savings|investment|debt_reduction|budget_optimization|tax_optimization|spending_reduction|income_increase|emergency_fund|retirement_planning|insurance|other",
      "priority": "low|medium|high|critical",
      "title": "Short, actionable title",
      "description": "Detailed description of the recommendation",
      "rationale": "Why this recommendation is important for this user",
      "estimated_savings": 1000.00,
      "estimated_time_to_implement": "1 week|1 month|3 months|6 months|1 year",
      "confidence_score": 0.85,
      "action_items": [
        {"step": 1, "action": "Specific action to take", "details": "Additional details"}
      ],
      "resources": [
        {"type": "article|tool|calculator", "title": "Resource title", "url": "https://example.com"}
      ]
    }
  ]
}

Make recommendations specific, actionable, and tailored to the user's financial situation. Consider their income, expenses, savings rate, and spending patterns."""
        
        return prompt
    
    async def generate_insights_from_recommendations(
        self,
        db: AsyncSession,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Generate insights based on user's recommendations"""
        recommendations = await self.get_user_recommendations(db, user_id, limit=100)
        
        if not recommendations:
            return []
        
        insights = []
        
        # Insight: Total potential savings
        total_savings = sum(r.estimated_savings or 0 for r in recommendations if r.is_pending)
        if total_savings > 0:
            insights.append({
                "type": "potential_savings",
                "title": "Potential Savings Opportunity",
                "description": f"You have ${total_savings:,.2f} in potential savings from pending recommendations.",
                "value": total_savings
            })
        
        # Insight: High priority recommendations
        high_priority = [r for r in recommendations if r.priority in [RecommendationPriority.HIGH, RecommendationPriority.CRITICAL] and r.is_pending]
        if high_priority:
            insights.append({
                "type": "high_priority",
                "title": "High Priority Actions",
                "description": f"You have {len(high_priority)} high-priority recommendations that need attention.",
                "count": len(high_priority)
            })
        
        # Insight: Completion rate
        completed = sum(1 for r in recommendations if r.is_completed)
        if len(recommendations) > 0:
            completion_rate = (completed / len(recommendations)) * 100
            insights.append({
                "type": "completion_rate",
                "title": "Recommendation Completion Rate",
                "description": f"You've completed {completion_rate:.1f}% of your recommendations.",
                "value": completion_rate
            })
        
        return insights


# Global recommendation service instance
recommendation_service = RecommendationService()


# Made with Bob