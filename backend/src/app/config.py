"""Application configuration."""

from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application name
    app_name: str = "OtakuHub"

    # Environment
    environment: str = "development"
    debug: bool = False

    # Database
    # Default uses PostgreSQL for dev/prod parity. Override with DATABASE_URL env var.
    # For local SQLite testing: sqlite+aiosqlite:///./test.db or set in conftest.py
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/otakuhub"
    db_pool_size: int = 20
    db_max_overflow: int = 30

    # CORS
    cors_origins: str = "http://localhost:8080"
    cors_allow_credentials: bool = True

    # JWT
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # External APIs
    anilist_client_id: str = "dummy-anilist-id"
    anilist_client_secret: str = "dummy-anilist-secret"
    mal_client_id: str = "dummy-mal-id"
    anikoto_sync_enabled: bool = False

    # Redis / Celery
    redis_url: str = "redis://localhost:6379/0"

    # Sentry
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.2  # 20% of transactions for perf tracing
    sentry_profiles_sample_rate: float = 0.2  # 20% for profiling

    # Apprise notifications
    apprise_urls: str = ""

    # Frontend
    frontend_url: str = "http://localhost:8080"

    # API prefix
    api_v1_prefix: str = "/api/v1"

    @property
    def cors_origins_list(self) -> List[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @model_validator(mode="after")
    def validate_security_defaults(self) -> "Settings":
        insecure_secrets = {"", "test-secret", "changeme", "dev-secret"}
        if self.jwt_secret.strip() in insecure_secrets:
            raise ValueError("JWT_SECRET must be explicitly set to a strong secret")

        if self.cors_origins.strip() == "*":
            raise ValueError("CORS_ORIGINS wildcard '*' is not allowed; set explicit origins")

        return self

# Create settings instance
settings = Settings()
