"""
Conversation and Message models for AI Copilot
Stores conversation history and context for personalized AI interactions
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class Conversation(Base):
    """
    Conversation model for AI copilot interactions
    Each conversation represents a session between user and AI
    """
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Conversation metadata
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)  # AI-generated summary of conversation
    
    # Context and state
    context = Column(JSON, nullable=True)  # Store conversation context (financial data references, etc.)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_message_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")
    intent_logs = relationship("IntentLog", back_populates="conversation", cascade="all, delete-orphan")
    compliance_violations = relationship("ComplianceViolation", back_populates="conversation", cascade="all, delete-orphan")
    escalations = relationship("Escalation", back_populates="conversation", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation {self.id}: {self.title}>"
    
    @property
    def message_count(self) -> int:
        """Get the number of messages in this conversation"""
        return len(self.messages) if self.messages else 0
    
    @property
    def is_recent(self) -> bool:
        """Check if conversation was active in the last 24 hours"""
        if not self.last_message_at:
            return False
        time_diff = datetime.utcnow() - self.last_message_at
        return time_diff.total_seconds() < 86400  # 24 hours


class Message(Base):
    """
    Message model for individual messages in a conversation
    Stores both user messages and AI responses
    """
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    
    # Metadata
    tokens_used = Column(Integer, nullable=True)  # Track token usage for cost management
    model = Column(String(50), nullable=True)  # Which model was used for this response
    message_metadata = Column(JSON, nullable=True)  # Additional metadata (function calls, etc.)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id}: {self.role}>"
    
    @property
    def is_user_message(self) -> bool:
        """Check if message is from user"""
        return self.role == "user"
    
    @property
    def is_assistant_message(self) -> bool:
        """Check if message is from AI assistant"""
        return self.role == "assistant"
    
    @property
    def preview(self) -> str:
        """Get a preview of the message content (first 100 chars)"""
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."


# Made with Bob