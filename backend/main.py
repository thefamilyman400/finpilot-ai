"""
FinPilot AI Backend - Main Application Entry Point
FastAPI application with authentication, CORS, and API routes
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from app.api.v1 import api_router
from app.db.session import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    print("[STARTUP] Starting FinPilot AI Backend...")
    print(f"[INFO] Environment: {settings.ENVIRONMENT}")
    print(f"[INFO] Debug Mode: {settings.DEBUG}")
    
    # Initialize database (create tables if they don't exist)
    # Note: In production, use Alembic migrations instead
    if settings.DEBUG:
        await init_db()
        print("[SUCCESS] Database initialized")
    
    yield
    
    # Shutdown
    print("[SHUTDOWN] Shutting down FinPilot AI Backend...")
    await close_db()
    print("[SUCCESS] Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered financial platform with intelligent guidance through copilots, dashboards, and autonomous workflows",
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "FinPilot AI Backend API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
    }


# Include API v1 routes
app.include_router(api_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    if settings.DEBUG:
        # In debug mode, show detailed error
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__,
            }
        )
    else:
        # In production, hide error details
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )

# Made with Bob
