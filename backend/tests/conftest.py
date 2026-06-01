"""
Pytest Configuration and Fixtures
Shared test fixtures for all tests
"""
import asyncio
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.db.base import Base
from app.core.security import get_password_hash, create_access_token
from app.models.user import User
from app.models.account import FinancialAccount, AccountType
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from main import app
from config import settings


# Test Database URL (use separate test database with async driver)
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/finpilot", "/finpilot-test").replace("postgresql://", "postgresql+asyncpg://")


# Global engine for reuse
_test_engine = None


async def get_test_engine():
    """Get or create test engine"""
    global _test_engine
    if _test_engine is None:
        _test_engine = create_async_engine(
            TEST_DATABASE_URL,
            echo=False,
            poolclass=NullPool,
            pool_pre_ping=True,
        )
        # Create tables
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    return _test_engine


@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine"""
    engine = await get_test_engine()
    yield engine


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a new database session for each test with transaction rollback"""
    connection = await test_engine.connect()
    transaction = await connection.begin()
    
    async_session = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    session = async_session()
    
    yield session
    
    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database dependency"""
    from app.core.dependencies import get_db
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user with unique email per test"""
    import uuid
    user = User(
        email=f"test-{uuid.uuid4()}@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(test_user: User) -> str:
    """Create JWT token for test user"""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def auth_headers(test_user_token: str) -> dict:
    """Create authorization headers"""
    return {"Authorization": f"Bearer {test_user_token}"}


@pytest_asyncio.fixture
async def test_account(db_session: AsyncSession, test_user: User) -> FinancialAccount:
    """Create a test financial account"""
    account = FinancialAccount(
        user_id=test_user.id,
        account_type=AccountType.CURRENT,
        institution_name="Test Bank",
        account_name="Test Checking",
        balance=1000.00,
        currency="USD",
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest_asyncio.fixture
async def test_transaction(
    db_session: AsyncSession,
    test_user: User,
    test_account: FinancialAccount
) -> Transaction:
    """Create a test transaction"""
    from datetime import datetime
    
    transaction = Transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        transaction_date=datetime.utcnow(),
        amount=50.00,
        transaction_type=TransactionType.DEBIT,
        category=TransactionCategory.GROCERIES,
        merchant_name="Test Store",
        description="Test purchase",
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)
    return transaction


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the AI assistant."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User",
    }


@pytest.fixture
def sample_account_data():
    """Sample account creation data"""
    return {
        "account_type": "checking",
        "institution_name": "Sample Bank",
        "account_name": "My Checking",
        "balance": 5000.00,
        "currency": "USD",
    }


@pytest.fixture
def sample_transaction_data(test_account: FinancialAccount):
    """Sample transaction creation data"""
    from datetime import datetime
    
    return {
        "account_id": str(test_account.id),
        "transaction_date": datetime.utcnow().isoformat(),
        "amount": 100.00,
        "transaction_type": "debit",
        "category": "groceries",
        "merchant_name": "Grocery Store",
        "description": "Weekly groceries",
    }


# Made with Bob