from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from src.app.models.enums import PartyStatus
from src.app.services.watch_party_service import WatchPartyService


class FakeResult:
    def __init__(self, *, all_value=None, one_value=None):
        self._all_value = [] if all_value is None else all_value
        self._one_value = one_value

    def all(self):
        return self._all_value

    def one_or_none(self):
        return self._one_value


@pytest.mark.asyncio
async def test_watch_party_read_queries() -> None:
    row = SimpleNamespace(id=uuid4())
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=row),
            FakeResult(all_value=[row]),
            FakeResult(all_value=[row]),
            FakeResult(all_value=[row]),
            FakeResult(one_value=2),
            FakeResult(all_value=[row]),
            FakeResult(one_value=4),
        ]
    )

    svc = WatchPartyService(session)
    uid = uuid4()
    gid = uuid4()

    assert await svc.get_watch_party(row.id) is row
    assert await svc.get_user_watch_parties(uid, limit=5) == [row]
    assert await svc.get_upcoming_watch_parties(group_id=gid, limit=5) == [row]
    assert await svc.get_upcoming_watch_parties_for_user(user_id=uid, group_id=None, limit=5, offset=0) == [row]
    assert await svc.count_upcoming_watch_parties_for_user(user_id=uid, group_id=None) == 2
    assert await svc.get_rsvps_for_party(uuid4()) == [row]
    with pytest.raises(AttributeError):
        await svc.get_party_attendee_count(uuid4())


@pytest.mark.asyncio
async def test_watch_party_group_membership_checks() -> None:
    uid = uuid4()
    gid = uuid4()

    # upcoming_for_user membership denied
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc = WatchPartyService(session)
    with pytest.raises(PermissionError):
        await svc.get_upcoming_watch_parties_for_user(user_id=uid, group_id=gid, limit=5, offset=0)

    # count membership denied
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc = WatchPartyService(session)
    with pytest.raises(PermissionError):
        await svc.count_upcoming_watch_parties_for_user(user_id=uid, group_id=gid)


@pytest.mark.asyncio
async def test_watch_party_create_update_delete_paths() -> None:
    uid = uuid4()
    gid = uuid4()
    mid = uuid4()
    now = datetime.now(UTC)

    # create simple
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = WatchPartyService(session)
    out = await svc.create_watch_party(uid, gid, mid, "title", now)
    assert out is not None

    # create_for_group_member permission denied
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc = WatchPartyService(session)
    with pytest.raises(PermissionError):
        await svc.create_watch_party_for_group_member(host_user_id=uid, group_id=gid, media_id=mid, scheduled_at=now)

    # create_for_group_member integrity error
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=SimpleNamespace(id=uid)))
    session.add = MagicMock()
    session.commit = AsyncMock(side_effect=IntegrityError("s", "p", Exception("x")))
    session.rollback = AsyncMock()
    svc = WatchPartyService(session)
    with pytest.raises(ValueError):
        await svc.create_watch_party_for_group_member(host_user_id=uid, group_id=gid, media_id=mid, scheduled_at=now)

    # create_for_group_member success timezone normalization
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=SimpleNamespace(id=uid)))
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = WatchPartyService(session)
    out = await svc.create_watch_party_for_group_member(host_user_id=uid, group_id=gid, media_id=mid, scheduled_at=now)
    assert out is not None

    # update not found then success — uses _watch_party_repo.get_by_id(), not self.get_watch_party()
    session = MagicMock()
    svc = WatchPartyService(session)
    svc._watch_party_repo.get_by_id = AsyncMock(side_effect=[None, SimpleNamespace(title="x")])
    assert await svc.update_watch_party(uuid4(), {"title": "y"}) is None
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    updated = await svc.update_watch_party(uuid4(), {"title": "y"})
    assert updated.title == "y"

    # delete false then true
    svc._watch_party_repo.get_by_id = AsyncMock(side_effect=[None, SimpleNamespace(deleted_at=None)])
    svc._watch_party_repo.soft_delete = AsyncMock(return_value=True)
    assert await svc.delete_watch_party(uuid4()) is False
    assert await svc.delete_watch_party(uuid4()) is True


@pytest.mark.asyncio
async def test_watch_party_rsvp_paths() -> None:
    party_id = uuid4()
    user_id = uuid4()

    # update existing RSVP
    existing = SimpleNamespace(status="pending", responded_at=None)
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=existing))
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = WatchPartyService(session)
    out = await svc.rsvp_to_watch_party(party_id, user_id, status="attending")
    assert out.status == "attending"

    # create new RSVP
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = WatchPartyService(session)
    out = await svc.rsvp_to_watch_party(party_id, user_id, status="pending")
    assert out is not None

    # group member wrapper: not found, not member, success
    # rsvp_to_watch_party_for_group_member calls self._watch_party_repo.get_by_id()
    svc = WatchPartyService(MagicMock())
    svc._watch_party_repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(LookupError):
        await svc.rsvp_to_watch_party_for_group_member(party_id=party_id, user_id=user_id, status="attending")

    party = SimpleNamespace(id=party_id, group_id=uuid4(), status=PartyStatus.scheduled)
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc = WatchPartyService(session)
    svc._watch_party_repo.get_by_id = AsyncMock(return_value=party)
    with pytest.raises(PermissionError):
        await svc.rsvp_to_watch_party_for_group_member(party_id=party_id, user_id=user_id, status="attending")

    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=SimpleNamespace(id=uuid4())))
    svc = WatchPartyService(session)
    svc._watch_party_repo.get_by_id = AsyncMock(return_value=party)
    svc.rsvp_to_watch_party = AsyncMock(return_value=SimpleNamespace(status="attending"))
    out = await svc.rsvp_to_watch_party_for_group_member(party_id=party_id, user_id=user_id, status="attending")
    assert out.status == "attending"
