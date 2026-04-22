"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str
    
    # Redis configuration
    REDIS_URL: str
    
    # JWT configuration
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # External API credentials
    ANILIST_CLIENT_ID: str
    ANILIST_CLIENT_SECRET: str
    MAL_CLIENT_ID: str
    
    # Apprise notification URLs (comma separated)
    APPRISE_URLS: str = ""
    
    # Frontend configuration
    FRONTEND_URL: str = "http://localhost:8080"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8080"]
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()