"""
Pydantic schemas for Conversation and Message models
Used for request/response validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Message Schemas
# ============================================================================

class MessageBase(BaseModel):
    """Base schema for Message"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")


class MessageCreate(MessageBase):
    """Schema for creating a new message"""
    conversation_id: UUID = Field(..., description="ID of the conversation")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: UUID
    conversation_id: UUID
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(None, alias="message_metadata")
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MessagePreview(BaseModel):
    """Lightweight message preview"""
    id: UUID
    role: str
    preview: str = Field(..., description="First 100 characters of content")
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Conversation Schemas
# ============================================================================

class ConversationBase(BaseModel):
    """Base schema for Conversation"""
    title: str = Field(..., min_length=1, max_length=255, description="Conversation title")


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation"""
    context: Optional[Dict[str, Any]] = Field(None, description="Initial context")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    summary: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""
    id: UUID
    user_id: UUID
    summary: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_message_at: datetime
    message_count: int = Field(..., description="Number of messages in conversation")
    is_recent: bool = Field(..., description="Active in last 24 hours")
    
    model_config = ConfigDict(from_attributes=True)


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with full message history"""
    messages: List[MessageResponse] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list"""
    conversations: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Chat/Copilot Schemas
# ============================================================================

class ChatMessage(BaseModel):
    """Schema for sending a chat message"""
    message: str = Field(..., min_length=1, description="User message to AI copilot")
    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (optional)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for AI")


class ChatResponse(BaseModel):
    """Schema for AI chat response"""
    conversation_id: UUID
    user_message: MessageResponse
    assistant_message: MessageResponse
    conversation_title: str
    tokens_used: int = Field(..., description="Total tokens used in this exchange")


class QuickAnalysisRequest(BaseModel):
    """Schema for quick financial analysis request"""
    query: str = Field(..., min_length=1, description="Analysis query")
    account_ids: Optional[List[UUID]] = Field(None, description="Specific accounts to analyze")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range for analysis")


class QuickAnalysisResponse(BaseModel):
    """Schema for quick analysis response"""
    analysis: str = Field(..., description="AI-generated analysis")
    insights: List[str] = Field(default_factory=list, description="Key insights")
    recommendations: List[str] = Field(default_factory=list, description="Quick recommendations")
    data_points: Optional[Dict[str, Any]] = Field(None, description="Supporting data")
    tokens_used: int


class ConversationSummaryRequest(BaseModel):
    """Schema for requesting conversation summary"""
    conversation_id: UUID


class ConversationSummaryResponse(BaseModel):
    """Schema for conversation summary"""
    conversation_id: UUID
    summary: str
    key_topics: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)


# ============================================================================
# Context Management Schemas
# ============================================================================

class FinancialContext(BaseModel):
    """Schema for financial context passed to AI"""
    total_balance: Optional[float] = None
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    savings_rate: Optional[float] = None
    debt_total: Optional[float] = None
    recent_transactions: Optional[List[Dict[str, Any]]] = None
    account_summary: Optional[Dict[str, Any]] = None
    goals: Optional[List[Dict[str, Any]]] = None


class ConversationContext(BaseModel):
    """Schema for full conversation context"""
    user_profile: Optional[Dict[str, Any]] = None
    financial_context: Optional[FinancialContext] = None
    recent_recommendations: Optional[List[Dict[str, Any]]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


# Made with Bob