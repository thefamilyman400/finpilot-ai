"""
API endpoints for AI Copilot functionality
Handles conversations, chat, and quick analysis
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationWithMessages,
    ConversationListResponse,
    ChatMessage,
    ChatResponse,
    QuickAnalysisRequest,
    QuickAnalysisResponse,
    MessageResponse,
)
from app.services.ai_service import ai_service


router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


def conversation_to_response(conversation: Conversation, message_count: int = 0) -> ConversationResponse:
    """
    Helper function to convert Conversation model to ConversationResponse schema
    
    Args:
        conversation: The Conversation model instance
        message_count: Pre-calculated message count to avoid lazy loading
    """
    # Calculate is_recent
    is_recent = False
    if conversation.last_message_at:
        time_diff = datetime.utcnow() - conversation.last_message_at
        is_recent = time_diff < timedelta(hours=24)
    
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        summary=conversation.summary,
        context=conversation.context,
        is_active=conversation.is_active,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=conversation.last_message_at,
        message_count=message_count,
        is_recent=is_recent
    )


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_copilot(
    chat_request: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with AI copilot
    
    - Creates a new conversation if conversation_id is not provided
    - Adds message to existing conversation if conversation_id is provided
    - Returns both user and assistant messages
    """
    try:
        result = await ai_service.chat(
            db=db,
            user_id=str(current_user.id),
            message=chat_request.message,
            conversation_id=str(chat_request.conversation_id) if chat_request.conversation_id else None,
            include_financial_context=chat_request.context is None or chat_request.context.get("include_financial_context", True)
        )
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            user_message=result["user_message"],
            assistant_message=result["assistant_message"],
            conversation_title=result["conversation_title"],
            tokens_used=result["tokens_used"]
        )
    except ValueError as e:
        error_text = str(e)
        
        # Handle quota exceeded errors
        if "quota exceeded" in error_text.lower() or "rate limit" in error_text.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_text
            )
        
        # Handle service unavailable errors
        if "temporarily unavailable" in error_text.lower() or "high demand" in error_text.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_text
            )
        
        # Handle conversation not found
        if "conversation not found" in error_text.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_text
            )
        
        # Other ValueError cases
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_text
        )
    except Exception as e:
        # Log full exception for diagnostics
        print(f"Copilot endpoint error (full): {repr(e)}")
        error_text = str(e)
        
        # Handle various AI service errors
        if "quota exceeded" in error_text.lower() or "rate limit" in error_text.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI service rate limit reached. Please try again in a few moments."
            )
        if "insufficient_quota" in error_text or "Error code: 429" in error_text:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI service quota exceeded. Please try again later."
            )
        if "model_not_found" in error_text or "does not exist or you do not have access to it" in error_text:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service unavailable: configured model is not accessible."
            )
        
        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat: {error_text}"
        )


@router.post("/quick-analysis", response_model=QuickAnalysisResponse, status_code=status.HTTP_200_OK)
async def get_quick_analysis(
    analysis_request: QuickAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a quick financial analysis without creating a conversation
    
    - Analyzes user's financial data based on the query
    - Returns insights and recommendations
    - Does not save to conversation history
    """
    try:
        result = await ai_service.generate_quick_analysis(
            db=db,
            user_id=str(current_user.id),
            query=analysis_request.query
        )
        
        return QuickAnalysisResponse(
            analysis=result["analysis"],
            insights=result["insights"],
            recommendations=result["recommendations"],
            data_points=result.get("financial_context"),
            tokens_used=result["tokens_used"]
        )
    except ValueError as e:
        error_text = str(e)
        
        # Handle quota exceeded errors
        if "quota exceeded" in error_text.lower() or "rate limit" in error_text.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_text
            )
        
        # Handle service unavailable errors
        if "temporarily unavailable" in error_text.lower() or "high demand" in error_text.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_text
            )
        
        # Other ValueError cases
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_text
        )
    except Exception as e:
        # Log full exception for diagnostics
        print(f"Quick analysis endpoint error (full): {repr(e)}")
        error_text = str(e)
        
        # Handle various AI service errors
        if "quota exceeded" in error_text.lower() or "rate limit" in error_text.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI service rate limit reached. Please try again in a few moments."
            )
        if "insufficient_quota" in error_text or "Error code: 429" in error_text:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="AI service quota exceeded. Please try again later."
            )
        if "model_not_found" in error_text or "does not exist or you do not have access to it" in error_text:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service unavailable: configured model is not accessible."
            )
        
        # Generic error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analysis: {error_text}"
        )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all conversations for the current user
    
    - Returns paginated list of conversations
    - Ordered by most recent activity
    """
    conversations = await ai_service.get_user_conversations(
        db=db,
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )
    
    # Get total count
    from sqlalchemy import select, func
    from app.models.conversation import Conversation
    
    count_result = await db.execute(
        select(func.count(Conversation.id)).where(
            Conversation.user_id == current_user.id
        )
    )
    total = count_result.scalar()
    
    # Convert conversations to response format
    conversation_responses = []
    for conv in conversations:
        # Count messages for this conversation without lazy loading
        from app.models.conversation import Message
        msg_count_result = await db.execute(
            select(func.count(Message.id)).where(Message.conversation_id == conv.id)
        )
        msg_count = msg_count_result.scalar() or 0
        conversation_responses.append(conversation_to_response(conv, msg_count))
    
    return ConversationListResponse(
        conversations=conversation_responses,
        total=total or 0,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=((total or 0) + limit - 1) // limit
    )


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new conversation
    
    - Creates an empty conversation with a title
    - Can include initial context
    """
    conversation = await ai_service.create_conversation(
        db=db,
        user_id=str(current_user.id),
        title=conversation_data.title,
        context=conversation_data.context
    )
    
    # New conversation has 0 messages
    return conversation_to_response(conversation, message_count=0)


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific conversation with full message history
    
    - Returns conversation details and all messages
    - Only accessible by conversation owner
    """
    conversation = await ai_service.get_conversation(
        db=db,
        conversation_id=str(conversation_id),
        user_id=str(current_user.id)
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    messages = await ai_service.get_conversation_history(
        db=db,
        conversation_id=str(conversation_id)
    )
    
    # Calculate is_recent
    is_recent = False
    if conversation.last_message_at:
        time_diff = datetime.utcnow() - conversation.last_message_at
        is_recent = time_diff < timedelta(hours=24)
    
    # Convert messages manually to avoid lazy loading issues
    message_responses = []
    for msg in messages:
        message_responses.append(MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            role=msg.role,
            content=msg.content,
            tokens_used=msg.tokens_used,
            model=msg.model,
            metadata=msg.message_metadata,  # Note: model field is message_metadata
            created_at=msg.created_at
        ))
    
    # Convert to response model
    conversation_dict = {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "summary": conversation.summary,
        "context": conversation.context,
        "is_active": conversation.is_active,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "last_message_at": conversation.last_message_at,
        "message_count": len(messages),
        "is_recent": is_recent,
        "messages": message_responses
    }
    
    return ConversationWithMessages(**conversation_dict)


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    conversation_update: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a conversation
    
    - Can update title, summary, context, or active status
    - Only accessible by conversation owner
    """
    conversation = await ai_service.get_conversation(
        db=db,
        conversation_id=str(conversation_id),
        user_id=str(current_user.id)
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Update fields
    update_data = conversation_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conversation, key, value)
    
    await db.commit()
    await db.refresh(conversation)
    
    # Count messages for this conversation
    from app.models.conversation import Message
    msg_count_result = await db.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation.id)
    )
    msg_count = msg_count_result.scalar() or 0
    
    return conversation_to_response(conversation, msg_count)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation
    
    - Permanently deletes conversation and all messages
    - Only accessible by conversation owner
    """
    conversation = await ai_service.get_conversation(
        db=db,
        conversation_id=str(conversation_id),
        user_id=str(current_user.id)
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    await db.delete(conversation)
    await db.commit()
    
    return None


# Made with Bob