"""
AI Copilot Tests
Tests for AI chat, conversations, and quick analysis
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.conversation import Conversation, Message


@pytest.fixture
def mock_openai_chat_response():
    """Mock OpenAI chat completion response"""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="This is a helpful financial advice response from the AI assistant."
            )
        )
    ]
    mock_response.usage = MagicMock(total_tokens=150)
    return mock_response


@pytest.fixture
async def test_conversation(db_session: AsyncSession, test_user: User) -> Conversation:
    """Create a test conversation"""
    conversation = Conversation(
        user_id=test_user.id,
        title="Test Conversation",
        context={"test": "context"}
    )
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)
    return conversation


@pytest.fixture
async def test_message(
    db_session: AsyncSession,
    test_conversation: Conversation
) -> Message:
    """Create a test message"""
    message = Message(
        conversation_id=test_conversation.id,
        role="user",
        content="Test message content"
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message


@pytest.mark.ai
@pytest.mark.asyncio
class TestChatEndpoint:
    """Test AI chat endpoint"""
    
    @patch('app.services.ai_service.ai_service.client')
    async def test_chat_new_conversation(
        self,
        mock_client,
        client: AsyncClient,
        auth_headers: dict,
        mock_openai_chat_response
    ):
        """Test chat with new conversation creation"""
        # Setup mock
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_chat_response)
        
        chat_data = {
            "message": "What's my current financial situation?"
        }
        
        response = await client.post(
            "/api/v1/copilot/chat",
            json=chat_data,
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "user_message" in data
        assert "assistant_message" in data
        assert "conversation_title" in data
        assert data["tokens_used"] == 150
    
    @patch('app.services.ai_service.ai_service.client')
    async def test_chat_existing_conversation(
        self,
        mock_client,
        client: AsyncClient,
        auth_headers: dict,
        test_conversation: Conversation,
        mock_openai_chat_response
    ):
        """Test chat with existing conversation"""
        # Setup mock
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_chat_response)
        
        chat_data = {
            "message": "Tell me more about my spending",
            "conversation_id": str(test_conversation.id)
        }
        
        response = await client.post(
            "/api/v1/copilot/chat",
            json=chat_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["conversation_id"] == str(test_conversation.id)
    
    async def test_chat_unauthorized(
        self,
        client: AsyncClient
    ):
        """Test chat without authentication"""
        chat_data = {
            "message": "Test message"
        }
        
        response = await client.post(
            "/api/v1/copilot/chat",
            json=chat_data
        )
        
        assert response.status_code == 401
    
    async def test_chat_nonexistent_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test chat with non-existent conversation ID"""
        import uuid
        
        chat_data = {
            "message": "Test message",
            "conversation_id": str(uuid.uuid4())
        }
        
        response = await client.post(
            "/api/v1/copilot/chat",
            json=chat_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    @patch('app.services.ai_service.AsyncOpenAI')
    async def test_chat_openai_quota_exceeded(
        self,
        mock_openai_class,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test chat when OpenAI quota is exceeded"""
        # Setup mock to raise quota error
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("Error code: 429 - insufficient_quota")
        )
        mock_openai_class.return_value = mock_client
        
        chat_data = {
            "message": "Test message"
        }
        
        response = await client.post(
            "/api/v1/copilot/chat",
            json=chat_data,
            headers=auth_headers
        )
        
        assert response.status_code == 503
        assert "quota" in response.json()["detail"].lower()


@pytest.mark.ai
@pytest.mark.asyncio
class TestQuickAnalysis:
    """Test quick analysis endpoint"""
    
    @patch('app.services.ai_service.ai_service.client')
    async def test_quick_analysis_success(
        self,
        mock_client,
        client: AsyncClient,
        auth_headers: dict,
        mock_openai_chat_response
    ):
        """Test successful quick analysis"""
        # Setup mock
        mock_client.chat.completions.create = AsyncMock(return_value=mock_openai_chat_response)
        
        analysis_data = {
            "query": "Analyze my spending patterns"
        }
        
        response = await client.post(
            "/api/v1/copilot/quick-analysis",
            json=analysis_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "insights" in data
        assert "recommendations" in data
        assert "tokens_used" in data
    
    async def test_quick_analysis_unauthorized(
        self,
        client: AsyncClient
    ):
        """Test quick analysis without authentication"""
        analysis_data = {
            "query": "Test query"
        }
        
        response = await client.post(
            "/api/v1/copilot/quick-analysis",
            json=analysis_data
        )
        
        assert response.status_code == 401


@pytest.mark.ai
@pytest.mark.asyncio
class TestConversationManagement:
    """Test conversation CRUD operations"""
    
    async def test_create_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test creating a new conversation"""
        conversation_data = {
            "title": "My Financial Planning",
            "context": {"topic": "retirement"}
        }
        
        response = await client.post(
            "/api/v1/copilot/conversations",
            json=conversation_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == conversation_data["title"]
        assert "id" in data
        assert data["is_active"] is True
    
    async def test_list_conversations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_conversation: Conversation
    ):
        """Test listing user conversations"""
        response = await client.get(
            "/api/v1/copilot/conversations",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert "total" in data
        assert isinstance(data["conversations"], list)
        assert len(data["conversations"]) >= 1
    
    async def test_list_conversations_pagination(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test conversation pagination"""
        response = await client.get(
            "/api/v1/copilot/conversations?skip=0&limit=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
    
    async def test_get_conversation_by_id(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_conversation: Conversation,
        test_message: Message
    ):
        """Test getting conversation with messages"""
        response = await client.get(
            f"/api/v1/copilot/conversations/{test_conversation.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_conversation.id)
        assert data["title"] == test_conversation.title
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    async def test_get_nonexistent_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test getting non-existent conversation"""
        import uuid
        fake_id = uuid.uuid4()
        
        response = await client.get(
            f"/api/v1/copilot/conversations/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_update_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_conversation: Conversation
    ):
        """Test updating conversation"""
        update_data = {
            "title": "Updated Title",
            "summary": "This is a summary"
        }
        
        response = await client.put(
            f"/api/v1/copilot/conversations/{test_conversation.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["summary"] == update_data["summary"]
    
    async def test_update_nonexistent_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test updating non-existent conversation"""
        import uuid
        fake_id = uuid.uuid4()
        
        response = await client.put(
            f"/api/v1/copilot/conversations/{fake_id}",
            json={"title": "Test"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_delete_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test deleting conversation"""
        # Create a conversation to delete
        conversation = Conversation(
            user_id=test_user.id,
            title="To Delete"
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        response = await client.delete(
            f"/api/v1/copilot/conversations/{conversation.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
    
    async def test_delete_nonexistent_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test deleting non-existent conversation"""
        import uuid
        fake_id = uuid.uuid4()
        
        response = await client.delete(
            f"/api/v1/copilot/conversations/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404


@pytest.mark.ai
@pytest.mark.asyncio
class TestConversationAuthorization:
    """Test conversation authorization"""
    
    async def test_cannot_access_other_user_conversation(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_user: User
    ):
        """Test that users cannot access other users' conversations"""
        from app.core.security import get_password_hash, create_access_token
        from app.models.user import User
        
        # Create another user
        other_user = User(
            email="other@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Other User",
            is_active=True,
            is_verified=True
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)
        
        # Create conversation for first user
        conversation = Conversation(
            user_id=test_user.id,
            title="Private Conversation"
        )
        db_session.add(conversation)
        await db_session.commit()
        await db_session.refresh(conversation)
        
        # Try to access with other user's token
        other_token = create_access_token(data={"sub": str(other_user.id)})
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        response = await client.get(
            f"/api/v1/copilot/conversations/{conversation.id}",
            headers=other_headers
        )
        
        assert response.status_code == 404


@pytest.mark.ai
@pytest.mark.asyncio
class TestConversationContext:
    """Test conversation context handling"""
    
    @patch('app.services.ai_service.ai_service.client')
    async def test_chat_with_financial_context(
        self,
        mock_client,
        client: AsyncClient,
        auth_headers: dict,
        test_account,
        test_transaction,
        mock_openai_chat_response
    ):
        """Test that chat includes financial context"""
        # Setup mock
        mock_create = AsyncMock(return_value=mock_openai_chat_response)
        mock_client.chat.completions.create = mock_create
        
        chat_data = {
            "message": "What's my spending like?",
            "context": {"include_financial_context": True}
        }
        
        response = await client.post(
            "/api/v1/copilot/chat",
            json=chat_data,
            headers=auth_headers
        )
        
        if response.status_code != 200:
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
        assert response.status_code == 200
        # Verify OpenAI was called
        assert mock_create.called
    
    @patch('app.services.ai_service.ai_service.client')
    async def test_chat_without_financial_context(
        self,
        mock_client,
        client: AsyncClient,
        auth_headers: dict,
        mock_openai_chat_response
    ):
        """Test chat without financial context"""
        # Setup mock
        mock_create = AsyncMock(return_value=mock_openai_chat_response)
        mock_client.chat.completions.create = mock_create
        
        chat_data = {
            "message": "General financial question",
            "context": {"include_financial_context": False}
        }
        
        response = await client.post(
            "/api/v1/copilot/chat",
            json=chat_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200


@pytest.mark.ai
@pytest.mark.asyncio
class TestMessageHistory:
    """Test message history functionality"""
    
    async def test_conversation_includes_message_history(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_conversation: Conversation
    ):
        """Test that conversation includes all messages"""
        # Add multiple messages
        messages = []
        for i in range(3):
            msg = Message(
                conversation_id=test_conversation.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}"
            )
            messages.append(msg)
            db_session.add(msg)
        
        await db_session.commit()
        
        response = await client.get(
            f"/api/v1/copilot/conversations/{test_conversation.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) >= 3
        assert data["message_count"] >= 3


# Made with Bob