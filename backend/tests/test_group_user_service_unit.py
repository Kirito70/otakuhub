from __future__ import annotations

from datetime import datetime
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


@pytest.mark.asyncio
async def test_group_service_core_paths() -> None:
    svc = GroupService()
    owner = SimpleNamespace(id=uuid4())
    payload = SimpleNamespace(name="g", description="d", is_private=True)

    db = MagicMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    out = await svc.create_group(db, owner, payload)
    assert out is not None

    group = SimpleNamespace(id=uuid4(), invite_code="abc", deleted_at=None)
    member = SimpleNamespace(group_id=group.id, user_id=owner.id, role="owner", joined_at=datetime.utcnow())

    # missing group
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(None))
    with pytest.raises(HTTPException):
        await svc.get_group_for_user(db, uuid4(), owner)

    # forbidden
    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(group), ScalarResult(None)])
    with pytest.raises(HTTPException):
        await svc.get_group_for_user(db, group.id, owner)

    # success
    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(group), ScalarResult(member)])
    got = await svc.get_group_for_user(db, group.id, owner)
    assert got is group

    # join invite not found
    db = MagicMock()
    db.execute = AsyncMock(return_value=ScalarResult(None))
    with pytest.raises(HTTPException):
        await svc.join_by_invite(db, "bad", owner)

    # join existing
    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(group), ScalarResult(member)])
    got = await svc.join_by_invite(db, group.invite_code, owner)
    assert got is member

    # join create
    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(group), ScalarResult(None)])
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    got = await svc.join_by_invite(db, group.invite_code, owner)
    assert got is not None

    # list members
    db = MagicMock()
    db.execute = AsyncMock(side_effect=[ScalarResult(group), ScalarResult(member), RowsResult([(SimpleNamespace(id=owner.id, username="u", display_name="d", avatar_url=None), member)])])
    members = await svc.list_members(db, group.id, owner)
    assert members[0]["username"] == "u"


@pytest.mark.asyncio
async def test_user_service_paths(monkeypatch) -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=RowsResult([SimpleNamespace(id=uuid4())]))
    session.commit = AsyncMock()

    svc = UserService(session)
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=SimpleNamespace(id=uuid4(), username="u", display_name="d", email="e", avatar_url=None, bio=None, timezone="UTC", is_active=True, created_at=datetime.utcnow(), updated_at=datetime.utcnow(), deleted_at=None))
    repo.get_by_username = AsyncMock(return_value=None)
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=SimpleNamespace(id=uuid4()))
    repo.update = AsyncMock(return_value=SimpleNamespace(id=uuid4()))
    repo.get_users_in_group = AsyncMock(return_value=[])
    repo.get_user_groups = AsyncMock(return_value=[])
    repo.get_active_users = AsyncMock(return_value=[])
    repo.search_users = AsyncMock(return_value=[])
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
