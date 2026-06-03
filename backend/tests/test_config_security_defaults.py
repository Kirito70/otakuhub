from __future__ import annotations

import os

import pytest

from src.app.config import Settings


def test_rejects_insecure_jwt_secret() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(jwt_secret="test-secret", cors_origins="http://localhost:8080")


def test_rejects_wildcard_cors() -> None:
    with pytest.raises(ValueError, match="CORS_ORIGINS"):
        Settings(jwt_secret="strong-secret-123", cors_origins="*")


def test_accepts_explicit_secure_values() -> None:
    cfg = Settings(
        jwt_secret="strong-secret-123",
        cors_origins="http://localhost:8080,https://otakuhub.local",
    )

    assert cfg.jwt_secret == "strong-secret-123"
    assert cfg.cors_origins_list == ["http://localhost:8080", "https://otakuhub.local"]
