"""
Recommendation model for AI-generated financial recommendations
Stores personalized suggestions and insights for users
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Float, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.base import Base


class RecommendationType(str, enum.Enum):
    """Types of recommendations the AI can generate"""
    SAVINGS = "savings"
    INVESTMENT = "investment"
    DEBT_REDUCTION = "debt_reduction"
    BUDGET_OPTIMIZATION = "budget_optimization"
    TAX_OPTIMIZATION = "tax_optimization"
    SPENDING_REDUCTION = "spending_reduction"
    INCOME_INCREASE = "income_increase"
    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT_PLANNING = "retirement_planning"
    INSURANCE = "insurance"
    OTHER = "other"


class RecommendationPriority(str, enum.Enum):
    """Priority levels for recommendations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationStatus(str, enum.Enum):
    """Status of a recommendation"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    EXPIRED = "expired"


class Recommendation(Base):
    """
    Recommendation model for AI-generated financial suggestions
    Each recommendation is a personalized suggestion based on user's financial data
    """
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Recommendation details
    type = Column(Enum(RecommendationType), nullable=False, index=True)
    priority = Column(Enum(RecommendationPriority), default=RecommendationPriority.MEDIUM, nullable=False)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING, nullable=False, index=True)
    
    # Content
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)  # Why this recommendation was made
    
    # Impact estimation
    estimated_savings = Column(Float, nullable=True)  # Estimated financial impact
    estimated_time_to_implement = Column(String(100), nullable=True)  # e.g., "1 week", "3 months"
    confidence_score = Column(Float, nullable=True)  # AI confidence in this recommendation (0-1)
    
    # Action items
    action_items = Column(JSON, nullable=True)  # List of specific steps to take
    resources = Column(JSON, nullable=True)  # Links, articles, tools to help implement
    
    # Metadata
    context = Column(JSON, nullable=True)  # Financial data that led to this recommendation
    ai_model = Column(String(50), nullable=True)  # Which AI model generated this
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    
    # User interaction
    viewed_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    user_notes = Column(Text, nullable=True)
    
    # Validity
    expires_at = Column(DateTime, nullable=True)  # Some recommendations may be time-sensitive
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    conversation = relationship("Conversation", backref="recommendations")
    
    def __repr__(self):
        return f"<Recommendation {self.id}: {self.type.value} - {self.status.value}>"
    
    @property
    def is_pending(self) -> bool:
        """Check if recommendation is pending user action"""
        return self.status == RecommendationStatus.PENDING
    
    @property
    def is_accepted(self) -> bool:
        """Check if recommendation was accepted by user"""
        return self.status == RecommendationStatus.ACCEPTED
    
    @property
    def is_completed(self) -> bool:
        """Check if recommendation was completed"""
        return self.status == RecommendationStatus.COMPLETED
    
    @property
    def is_expired(self) -> bool:
        """Check if recommendation has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def days_since_created(self) -> int:
        """Get number of days since recommendation was created"""
        time_diff = datetime.utcnow() - self.created_at
        return time_diff.days
    
    @property
    def priority_score(self) -> int:
        """Get numeric priority score for sorting"""
        priority_map = {
            RecommendationPriority.LOW: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.HIGH: 3,
            RecommendationPriority.CRITICAL: 4
        }
        return priority_map.get(self.priority, 0)
    
    def mark_viewed(self):
        """Mark recommendation as viewed"""
        if not self.viewed_at:
            self.viewed_at = datetime.utcnow()
    
    def accept(self):
        """Accept the recommendation"""
        self.status = RecommendationStatus.ACCEPTED
        self.accepted_at = datetime.utcnow()
    
    def reject(self, notes: Optional[str] = None):
        """Reject the recommendation"""
        self.status = RecommendationStatus.REJECTED
        self.rejected_at = datetime.utcnow()
        if notes:
            self.user_notes = notes
    
    def complete(self, notes: Optional[str] = None):
        """Mark recommendation as completed"""
        self.status = RecommendationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if notes:
            self.user_notes = notes


# Made with Bob