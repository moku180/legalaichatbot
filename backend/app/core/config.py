"""Application configuration using Pydantic Settings"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "Legal AI SaaS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost"]
    
    # Database
    POSTGRES_USER: str = "legalai"
    POSTGRES_PASSWORD: str = "legalai_password"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "legalai_db"
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Construct sync database URL for Alembic"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis (optional - graceful degradation if not available)
    REDIS_URL: Optional[str] = None  # Railway provides this
    REDIS_HOST: str = "localhost"
    REDIS_PORT: Optional[int] = 6379  # Made optional with default
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_CONNECTION_URL(self) -> Optional[str]:
        """Get Redis URL - supports both REDIS_URL and individual components"""
        # If REDIS_URL is provided (Railway style), use it
        if self.REDIS_URL:
            return self.REDIS_URL
        
        # If Redis is disabled or port is None, return None
        if self.REDIS_PORT is None:
            return None
            
        # Otherwise construct from individual components
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Celery (optional - not used in Railway deployment)
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    @property
    def CELERY_BROKER(self) -> Optional[str]:
        """Get Celery broker URL"""
        return self.CELERY_BROKER_URL or self.REDIS_CONNECTION_URL
    
    @property
    def CELERY_BACKEND(self) -> Optional[str]:
        """Get Celery result backend URL"""
        return self.CELERY_RESULT_BACKEND or self.REDIS_CONNECTION_URL
    
    @validator('REDIS_PORT', pre=True)
    def validate_redis_port(cls, v):
        """Convert empty string to None for REDIS_PORT"""
        if v == '' or v is None:
            return None
        return int(v) if isinstance(v, str) else v
    
    # Security
    SECRET_KEY: str = Field(default="INSECURE-DEFAULT-KEY-CHANGE-ME-IN-PRODUCTION-32CHARS", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # LLM Configuration - Google Gemini
    GEMINI_API_KEY: str = Field(..., min_length=20)
    GEMINI_MODEL: str = "models/gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    GEMINI_TEMPERATURE: float = 0.1
    GEMINI_MAX_TOKENS: int = 2000
    
    # Alternative LLM (optional)
    CUSTOM_LLM_ENDPOINT: Optional[str] = None
    CUSTOM_LLM_API_KEY: Optional[str] = None
    
    # RAG Configuration
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100
    RETRIEVAL_TOP_K: int = 5
    MMR_DIVERSITY_SCORE: float = 0.3
    VECTOR_STORE_PATH: str = "./data/vector_stores"
    
    # Document Storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".docx", ".txt"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_ENABLED: bool = True
    
    # Usage & Billing
    TRACK_USAGE: bool = True
    COST_PER_1K_INPUT_TOKENS: float = 0.01
    COST_PER_1K_OUTPUT_TOKENS: float = 0.03
    
    # Legal Compliance
    LEGAL_DISCLAIMER: str = "This platform provides general legal information and not legal advice. Consult a qualified attorney for specific legal matters."
    REFUSE_PERSONAL_ADVICE: bool = True
    REQUIRE_CITATIONS: bool = True
    MIN_CONFIDENCE_SCORE: float = 0.6
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
