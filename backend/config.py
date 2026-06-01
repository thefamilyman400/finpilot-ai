"""
Configuration settings for FinPilot AI Backend
Uses Pydantic Settings for environment variable management
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "FinPilot AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = Field(..., description="Redis connection string")
    
    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT encoding")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    # AI Configuration (Using Google Gemini)
    GOOGLE_API_KEY: str = Field(..., description="Google Gemini API key")
    GOOGLE_GEMINI_MODEL: str = "gemini-pro"
    OPENAI_TEMPERATURE: float = 0.7  # Temperature setting (reused for Gemini)
    OPENAI_MAX_TOKENS: int = 2000  # Max tokens setting (reused for Gemini)
    AI_CONVERSATION_MAX_HISTORY: int = 20
    AI_CONTEXT_WINDOW: int = 8000
    
    # File Upload & Document Processing
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB in bytes
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_FILE_TYPES: str = "pdf,docx,doc,txt,png,jpg,jpeg"
    DOCUMENT_RETENTION_DAYS: int = 365
    DOCUMENT_UPLOAD_DIR: str = "./uploads/documents"
    MAX_DOCUMENT_SIZE: int = 52428800  # 50MB in bytes
    TESSERACT_PATH: str = "C:/Program Files/Tesseract-OCR/tesseract.exe"
    
    @property
    def allowed_file_extensions(self) -> List[str]:
        """Get allowed file extensions as a list"""
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(",") if ext.strip()]
    
    # Celery & Background Tasks
    CELERY_BROKER_URL: str = Field(..., description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(..., description="Celery result backend URL")
    CELERY_TASK_ALWAYS_EAGER: bool = False
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 300  # 5 minutes
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 4
    
    # Simulation Settings
    SIMULATION_MAX_YEARS: int = 50
    SIMULATION_DEFAULT_INFLATION_RATE: float = 0.03
    SIMULATION_DEFAULT_RETURN_RATE: float = 0.07
    SIMULATION_MONTE_CARLO_ITERATIONS: int = 1000
    
    # Workflow Settings
    WORKFLOW_MAX_EXECUTIONS_PER_DAY: int = 100
    WORKFLOW_EXECUTION_TIMEOUT: int = 300  # 5 minutes
    WORKFLOW_RETRY_ATTEMPTS: int = 3
    WORKFLOW_RETRY_DELAY: int = 60  # seconds
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@finpilot.ai"
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    FRONTEND_URL: str = "http://localhost:3000"  # Frontend URL for email links
    
    # External APIs
    PLAID_CLIENT_ID: str = ""
    PLAID_SECRET: str = ""
    PLAID_ENV: str = "sandbox"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    @property
    def database_url_async(self) -> str:
        """Convert PostgreSQL URL to async version for SQLAlchemy"""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"


# Global settings instance
settings = Settings()

# Made with Bob
