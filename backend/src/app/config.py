"""Application configuration."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application name
    app_name: str = "OtakuHub"

    # Environment
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///:memory:"
    db_pool_size: int = 20
    db_max_overflow: int = 30

    # CORS
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True

    # JWT
    jwt_secret: str = "test-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # External APIs
    anilist_client_id: str = "dummy-anilist-id"
    anilist_client_secret: str = "dummy-anilist-secret"
    mal_client_id: str = "dummy-mal-id"

    # Apprise notifications
    apprise_urls: str = ""

    # Frontend
    frontend_url: str = "http://localhost:8080"

    # API prefix
    api_v1_prefix: str = "/api/v1"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()
