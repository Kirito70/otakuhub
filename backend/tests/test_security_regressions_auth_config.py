from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.app.config import Settings
from src.app.core.security import verify_password
from src.app.services.auth_service import AuthService


class ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class ScalarsListResult:
    def __init__(self, values):
        self._values = values

    def scalars(self):
        return self

    def all(self):
        return self._values


def test_settings_rejects_empty_jwt_secret() -> None:
    with pytest.raises(ValueError, match="JWT_SECRET"):
        Settings(jwt_secret="", cors_origins="http://localhost:8080")


def test_verify_password_rejects_wrong_password_for_legacy_hash() -> None:
    legacy_hash = "a" * 64
    assert verify_password("wrong", legacy_hash) is False


@pytest.mark.asyncio
async def test_refresh_reuse_still_fails_when_no_other_active_tokens() -> None:
    user_id = uuid4()
    reused = SimpleNamespace(user_id=user_id, revoked_at=datetime.utcnow(), expires_at=datetime.utcnow() + timedelta(days=1))

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(reused), ScalarsListResult([])])
    db.commit = AsyncMock()

    svc = AuthService()

    with pytest.raises(HTTPException) as exc:
        await svc.refresh(db, SimpleNamespace(refresh_token="reused"))

    assert exc.value.status_code == 401
    assert "reuse" in str(exc.value.detail).lower()
    db.commit.assert_awaited_once()
