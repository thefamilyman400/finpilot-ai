"""
Escalation and Ticket Models
Handles Human-in-the-Loop (HITL) workflows and support ticket management
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum

from app.db.base import Base


class EscalationPriority(str, Enum):
    """Priority levels for escalations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class EscalationStatus(str, Enum):
    """Status of escalation"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Escalation(Base):
    """Model for escalated conversations requiring human review"""
    
    __tablename__ = "escalations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Escalation details
    reason = Column(String(255), nullable=False)  # Why escalated
    priority = Column(
        SQLEnum(EscalationPriority, name="escalation_priority"),
        default=EscalationPriority.MEDIUM,
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum(EscalationStatus, name="escalation_status"),
        default=EscalationStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolution_action = Column(String(100), nullable=True)  # 'approved', 'modified', 'rejected'
    
    # Additional context
    escalation_context = Column(JSONB, nullable=True)  # Store relevant context
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="escalations")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    
    def __repr__(self):
        return f"<Escalation(id={self.id}, status={self.status}, priority={self.priority})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "reason": self.reason,
            "priority": self.priority.value if self.priority else None,
            "status": self.status.value if self.status else None,
            "assigned_to": str(self.assigned_to) if self.assigned_to else None,
            "resolution_notes": self.resolution_notes,
            "resolution_action": self.resolution_action,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class TicketPriority(str, Enum):
    """Priority levels for support tickets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, Enum):
    """Status of support ticket"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SupportTicket(Base):
    """Model for support tickets"""
    
    __tablename__ = "support_tickets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Ticket details
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True, index=True)
    
    # Issue information
    issue_type = Column(String(100), nullable=False, index=True)  # 'complaint', 'inquiry', 'technical', etc.
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Priority and status
    priority = Column(
        SQLEnum(TicketPriority, name="ticket_priority"),
        default=TicketPriority.MEDIUM,
        nullable=False,
        index=True
    )
    status = Column(
        SQLEnum(TicketStatus, name="ticket_status"),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True
    )
    
    # Assignment
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    department = Column(String(100), nullable=True)  # 'support', 'compliance', 'technical'
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolution_time_minutes = Column(Integer, nullable=True)  # Time to resolve
    
    # Additional data
    ticket_metadata = Column(JSONB, nullable=True)  # Store additional context
    tags = Column(JSONB, nullable=True)  # Tags for categorization
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="support_tickets")
    conversation = relationship("Conversation", back_populates="support_tickets")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    
    def __repr__(self):
        return f"<SupportTicket(number={self.ticket_number}, status={self.status})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "ticket_number": self.ticket_number,
            "user_id": str(self.user_id) if self.user_id else None,
            "conversation_id": str(self.conversation_id) if self.conversation_id else None,
            "issue_type": self.issue_type,
            "subject": self.subject,
            "description": self.description,
            "priority": self.priority.value if self.priority else None,
            "status": self.status.value if self.status else None,
            "assigned_to": str(self.assigned_to) if self.assigned_to else None,
            "department": self.department,
            "resolution": self.resolution,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }
    
    @staticmethod
    def generate_ticket_number() -> str:
        """Generate unique ticket number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = str(uuid.uuid4())[:6].upper()
        return f"TKT-{timestamp}-{random_suffix}"


# Made with Bob - Compliance-First AI Assistant