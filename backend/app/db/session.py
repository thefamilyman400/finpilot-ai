"""
Database session management
Handles async database connections and session lifecycle
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from config import settings


# Create async engine
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    # Use NullPool for serverless environments, otherwise use default QueuePool
    poolclass=NullPool if settings.ENVIRONMENT == "serverless" else None,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session
    
    Yields:
        AsyncSession: Database session
        
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database
    Create all tables if they don't exist
    
    Note: In production, use Alembic migrations instead
    """
    from app.db.base import Base
    
    async with engine.begin() as conn:
        # Import all models here to ensure they are registered with Base
        import app.models  # noqa: F401
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """
    Close database connections
    Should be called on application shutdown
    """
    await engine.dispose()

# Made with Bob
