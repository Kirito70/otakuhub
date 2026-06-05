from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from src.app.services.group_service import GroupService
from src.app.services.user_service import UserService


class ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar_one_or_none(self):
        return self._value


class RowsResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows

    def one_or_none(self):
        """Return first row or None (used by get_user_settings flow)."""
        return self._rows[0] if self._rows else None


@pytest.mark.asyncio
async def test_group_service_core_paths() -> None:
    svc = GroupService()
    owner = SimpleNamespace(id=uuid4())
    payload = SimpleNamespace(name="g", description="d", is_private=True)

    # Mock repositories to avoid QueryBuilder needing a real db_session.exec()
    mock_group_repo = MagicMock()
    mock_member_repo = MagicMock()
    svc._group_repo = lambda db: mock_group_repo
    svc._member_repo = lambda db: mock_member_repo

    db = MagicMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    out = await svc.create_group(db, owner, payload)
    assert out is not None

    group = SimpleNamespace(id=uuid4(), invite_code="abc", deleted_at=None)
    member = SimpleNamespace(
        group_id=group.id, user_id=owner.id, role="owner",
        joined_at=datetime.now(timezone.utc),
    )

    # missing group
    mock_group_repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(HTTPException):
        await svc.get_group_for_user(db, uuid4(), owner)

    # forbidden
    mock_group_repo.get_by_id = AsyncMock(return_value=group)
    mock_member_repo.is_member = AsyncMock(return_value=False)
    with pytest.raises(HTTPException):
        await svc.get_group_for_user(db, group.id, owner)

    # success
    mock_group_repo.get_by_id = AsyncMock(return_value=group)
    mock_member_repo.is_member = AsyncMock(return_value=True)
    got = await svc.get_group_for_user(db, group.id, owner)
    assert got is group

    # join invite not found
    mock_group_repo.get_by_invite_code = AsyncMock(return_value=None)
    with pytest.raises(HTTPException):
        await svc.join_by_invite(db, "bad", owner)

    # join existing
    mock_group_repo.get_by_invite_code = AsyncMock(return_value=group)
    mock_member_repo.is_member = AsyncMock(return_value=True)
    mock_member_repo.list_by_user = AsyncMock(return_value=[member])
    got = await svc.join_by_invite(db, group.invite_code, owner)
    assert got is member

    # join create
    mock_group_repo.get_by_invite_code = AsyncMock(return_value=group)
    mock_member_repo.is_member = AsyncMock(return_value=False)
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    got = await svc.join_by_invite(db, group.invite_code, owner)
    assert got is not None

    # list members — list_members uses db.execute() directly after get_group_for_user
    mock_group_repo.get_by_id = AsyncMock(return_value=group)
    mock_member_repo.is_member = AsyncMock(return_value=True)
    db.execute = AsyncMock(
        return_value=RowsResult(
            [(SimpleNamespace(id=owner.id, username="u", display_name="d", avatar_url=None), member)]
        )
    )
    members = await svc.list_members(db, group.id, owner)
    assert members[0]["username"] == "u"


@pytest.mark.asyncio
async def test_user_service_paths(monkeypatch) -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=RowsResult([]))
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    svc = UserService(session)
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=SimpleNamespace(id=uuid4(), username="u", display_name="d", email="e", avatar_url=None, bio=None, timezone="UTC", is_active=True, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), deleted_at=None))
    repo.get_by_username = AsyncMock(return_value=None)
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=SimpleNamespace(id=uuid4()))
    repo.update = AsyncMock(return_value=SimpleNamespace(id=uuid4()))
    repo.get_users_in_group = AsyncMock(return_value=[])
    repo.get_user_groups = AsyncMock(return_value=[])
    repo.get_active_users = AsyncMock(return_value=[])
    repo.search_users = AsyncMock(return_value=[])
    repo.get_all = AsyncMock(return_value=[SimpleNamespace(id=uuid4())])
    repo.delete = AsyncMock(side_effect=[False, True])
    svc._user_repository = repo

    monkeypatch.setattr("src.app.services.user_service.get_password_hash", lambda p: "hashed")

    assert await svc.get_user_by_id(uuid4()) is not None
    assert await svc.get_user_by_username("u") is None
    assert await svc.get_user_by_email("e") is None
    assert len(await svc.get_users(limit=5, offset=0)) == 1

    created = await svc.create_user({"username": "u", "password": "secret123"})
    assert created is not None
    updated = await svc.update_user(uuid4(), {"password": "secret123"})
    assert updated is not None

    # delete false and true
    svc.get_user_by_id = AsyncMock(side_effect=[None, SimpleNamespace(deleted_at=None)])
    assert await svc.delete_user(uuid4()) is False
    assert await svc.delete_user(uuid4()) is True

    svc.get_user_by_id = AsyncMock(return_value=None)
    profile = await svc.get_user_profile(uuid4())
    assert profile is None

    assert (await svc.get_user_settings(uuid4())).user_id is not None
    assert (await svc.update_user_settings(uuid4(), {})).user_id is not None
    assert await svc.get_users_in_group(uuid4(), 10, 0) == []
    assert await svc.get_user_groups(uuid4()) == []
    assert await svc.get_active_users(5) == []
    assert await svc.search_users("abc", 5) == []
