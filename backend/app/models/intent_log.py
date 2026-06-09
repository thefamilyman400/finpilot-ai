"""
Intent Log Model
Tracks all intent classifications for compliance auditing
"""
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base import Base


class IntentLog(Base):
    """Model for logging intent classifications"""
    
    __tablename__ = "intent_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)
    user_message = Column(Text, nullable=False)
    detected_intent = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=False)
    was_blocked = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    entities = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    conversation = relationship("Conversation", back_populates="intent_logs")
    
    def __repr__(self):
        return f"<IntentLog(id={self.id}, intent={self.detected_intent}, blocked={self.was_blocked})>"


class ComplianceViolation(Base):
    """Model for logging compliance violations"""
    
    __tablename__ = "compliance_violations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)
    violation_type = Column(String(100), nullable=False)
    ai_response = Column(Text, nullable=False)
    corrected_response = Column(Text, nullable=True)
    severity = Column(String(20), default="medium")  # low, medium, high
    violations = Column(JSONB, nullable=True)  # List of specific violations
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    conversation = relationship("Conversation", back_populates="compliance_violations")
    
    def __repr__(self):
        return f"<ComplianceViolation(id={self.id}, type={self.violation_type}, severity={self.severity})>"


# Made with Bob - Compliance-First AI Assistant