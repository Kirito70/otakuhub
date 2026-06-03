from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

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


@pytest.mark.asyncio
async def test_is_setup_required_true_when_no_user() -> None:
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(None))

    svc = AuthService()
    assert await svc.is_setup_required(db) is True


@pytest.mark.asyncio
async def test_is_setup_required_false_when_user_exists() -> None:
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(uuid4()))

    svc = AuthService()
    assert await svc.is_setup_required(db) is False


@pytest.mark.asyncio
async def test_register_blocks_when_setup_complete() -> None:
    db = MagicMock()
    svc = AuthService()
    svc.is_setup_required = AsyncMock(return_value=False)

    payload = SimpleNamespace(username="u", email="u@example.com", password="password123")
    with pytest.raises(HTTPException) as exc:
        await svc.register(db, payload)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_register_rejects_duplicate_user() -> None:
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(SimpleNamespace(id=uuid4())))

    svc = AuthService()
    svc.is_setup_required = AsyncMock(return_value=True)
    payload = SimpleNamespace(username="u", email="u@example.com", password="password123")

    with pytest.raises(HTTPException) as exc:
        await svc.register(db, payload)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_login_rejects_invalid_credentials() -> None:
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(None))

    svc = AuthService()
    payload = SimpleNamespace(username="missing", password="password123")

    with pytest.raises(HTTPException) as exc:
        await svc.login(db, payload)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_success_returns_tokens(monkeypatch) -> None:
    user = SimpleNamespace(id=uuid4(), password_hash="hashed")
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(user))
    db.add = MagicMock()
    db.commit = AsyncMock()

    monkeypatch.setattr("src.app.services.auth_service.verify_password", lambda p, h: True)
    monkeypatch.setattr("src.app.services.auth_service.needs_password_rehash", lambda h: False)
    monkeypatch.setattr("src.app.services.auth_service.create_access_token", lambda sub: f"access-{sub}")
    monkeypatch.setattr("src.app.services.auth_service.token_urlsafe", lambda n: "refresh-token")

    svc = AuthService()
    payload = SimpleNamespace(username="u", password="password123")
    out = await svc.login(db, payload)

    assert out.access_token.startswith("access-")
    assert out.refresh_token == "refresh-token"
    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_rehashes_legacy_password_on_success(monkeypatch) -> None:
    user = SimpleNamespace(id=uuid4(), password_hash="legacy-hash")
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(user))
    db.add = MagicMock()
    db.commit = AsyncMock()

    monkeypatch.setattr("src.app.services.auth_service.verify_password", lambda p, h: True)
    monkeypatch.setattr("src.app.services.auth_service.needs_password_rehash", lambda h: True)
    monkeypatch.setattr("src.app.services.auth_service.get_password_hash", lambda p: "bcrypt-upgraded")
    monkeypatch.setattr("src.app.services.auth_service.create_access_token", lambda sub: f"access-{sub}")
    monkeypatch.setattr("src.app.services.auth_service.token_urlsafe", lambda n: "refresh-token")

    svc = AuthService()
    _ = await svc.login(db, SimpleNamespace(username="u", password="password123"))

    assert user.password_hash == "bcrypt-upgraded"
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_rejects_missing_token_row() -> None:
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(None))

    svc = AuthService()
    payload = SimpleNamespace(refresh_token="x")

    with pytest.raises(HTTPException) as exc:
        await svc.refresh(db, payload)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rejects_revoked_or_expired() -> None:
    expired = SimpleNamespace(user_id=uuid4(), revoked_at=None, expires_at=datetime.utcnow() - timedelta(days=1))
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(expired))

    svc = AuthService()
    payload = SimpleNamespace(refresh_token="x")

    with pytest.raises(HTTPException) as exc:
        await svc.refresh(db, payload)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_reuse_revokes_all_active_user_tokens() -> None:
    user_id = uuid4()
    reused = SimpleNamespace(user_id=user_id, revoked_at=datetime.utcnow(), expires_at=datetime.utcnow() + timedelta(days=1))
    sibling_a = SimpleNamespace(revoked_at=None)
    sibling_b = SimpleNamespace(revoked_at=None)

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(reused), ScalarsListResult([sibling_a, sibling_b])])
    db.commit = AsyncMock()

    svc = AuthService()

    with pytest.raises(HTTPException) as exc:
        await svc.refresh(db, SimpleNamespace(refresh_token="reused"))

    assert exc.value.status_code == 401
    assert "reuse" in str(exc.value.detail).lower()
    assert sibling_a.revoked_at is not None
    assert sibling_b.revoked_at is not None
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_rejects_missing_user_for_token() -> None:
    row = SimpleNamespace(user_id=uuid4(), revoked_at=None, expires_at=datetime.utcnow() + timedelta(days=1))
    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(row), ScalarResult(None)])

    svc = AuthService()
    payload = SimpleNamespace(refresh_token="x")

    with pytest.raises(HTTPException) as exc:
        await svc.refresh(db, payload)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_success_rotates_token(monkeypatch) -> None:
    user_id = uuid4()
    row = SimpleNamespace(user_id=user_id, revoked_at=None, expires_at=datetime.utcnow() + timedelta(days=1))
    user = SimpleNamespace(id=user_id)

    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(row), ScalarResult(user)])
    db.add = MagicMock()
    db.commit = AsyncMock()

    monkeypatch.setattr("src.app.services.auth_service.create_access_token", lambda sub: f"access-{sub}")
    monkeypatch.setattr("src.app.services.auth_service.token_urlsafe", lambda n: "rotated-refresh")

    svc = AuthService()
    out = await svc.refresh(db, SimpleNamespace(refresh_token="incoming"))

    assert out.refresh_token == "rotated-refresh"
    assert row.revoked_at is not None
    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_logout_revokes_existing_token() -> None:
    row = SimpleNamespace(revoked_at=None)
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(row))
    db.commit = AsyncMock()

    svc = AuthService()
    await svc.logout(db, "refresh-token")

    assert row.revoked_at is not None
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_logout_noop_when_token_missing() -> None:
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(None))
    db.commit = AsyncMock()

    svc = AuthService()
    await svc.logout(db, "missing")

    db.commit.assert_not_called()
