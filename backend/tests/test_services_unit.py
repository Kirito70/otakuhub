from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.app.services.notification_service import NotificationService
from src.app.services.social_service import SocialService
from src.app.services.tracking_service import TrackingService
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
async def test_notification_mark_notifications_as_read_updates_only_unread() -> None:
    user_id = uuid4()
    n1 = SimpleNamespace(is_read=False, read_at=None)
    n2 = SimpleNamespace(is_read=False, read_at=None)

    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(all_value=[n1, n2]))
    session.commit = AsyncMock()

    service = NotificationService(session)
    updated = await service.mark_notifications_as_read(
        user_id=user_id,
        notification_ids=[uuid4(), uuid4()],
    )

    assert updated == 2
    assert n1.is_read is True and n2.is_read is True
    assert n1.read_at is not None and n2.read_at is not None
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_notification_mark_notifications_as_read_empty_ids_short_circuit() -> None:
    session = MagicMock()
    session.exec = AsyncMock()
    session.commit = AsyncMock()

    service = NotificationService(session)
    updated = await service.mark_notifications_as_read(user_id=uuid4(), notification_ids=[])

    assert updated == 0
    session.exec.assert_not_called()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_notification_get_preferences_creates_default_when_missing() -> None:
    user_id = uuid4()
    pref = SimpleNamespace(user_id=user_id)

    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=lambda obj: None)

    service = NotificationService(session)
    out = await service.get_notification_preferences(user_id=user_id)

    assert out.user_id == user_id
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_watch_party_rsvp_missing_party_raises_lookup_error() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))

    service = WatchPartyService(session)

    with pytest.raises(LookupError):
        await service.rsvp_to_watch_party_for_group_member(
            party_id=uuid4(),
            user_id=uuid4(),
            status="attending",
        )


@pytest.mark.asyncio
async def test_watch_party_rsvp_non_member_raises_permission_error() -> None:
    party = SimpleNamespace(id=uuid4(), group_id=uuid4(), deleted_at=None)
    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=party), FakeResult(one_value=None)])

    service = WatchPartyService(session)

    with pytest.raises(PermissionError):
        await service.rsvp_to_watch_party_for_group_member(
            party_id=party.id,
            user_id=uuid4(),
            status="attending",
        )


@pytest.mark.asyncio
async def test_watch_party_rsvp_member_delegates_to_plain_rsvp() -> None:
    party = SimpleNamespace(id=uuid4(), group_id=uuid4(), deleted_at=None)
    membership = SimpleNamespace(group_id=party.group_id, user_id=uuid4())
    expected = SimpleNamespace(status="attending")

    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=party), FakeResult(one_value=membership)])

    service = WatchPartyService(session)
    service.rsvp_to_watch_party = AsyncMock(return_value=expected)

    out = await service.rsvp_to_watch_party_for_group_member(
        party_id=party.id,
        user_id=membership.user_id,
        status="attending",
    )

    assert out is expected
    service.rsvp_to_watch_party.assert_awaited_once()


@pytest.mark.asyncio
async def test_watch_party_create_requires_group_membership() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))

    service = WatchPartyService(session)

    with pytest.raises(PermissionError):
        await service.create_watch_party_for_group_member(
            host_user_id=uuid4(),
            group_id=uuid4(),
            media_id=uuid4(),
            scheduled_at=datetime.utcnow(),
        )


@pytest.mark.asyncio
async def test_social_acknowledge_recommendation_missing_returns_none() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))

    service = SocialService(session)
    out = await service.acknowledge_recommendation(uuid4(), uuid4())

    assert out is None


@pytest.mark.asyncio
async def test_social_acknowledge_recommendation_wrong_owner_returns_none() -> None:
    recommendation = SimpleNamespace(to_user_id=uuid4(), is_acknowledged=False, acknowledged_at=None)
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=recommendation))

    service = SocialService(session)
    out = await service.acknowledge_recommendation(uuid4(), uuid4())

    assert out is None


@pytest.mark.asyncio
async def test_social_acknowledge_recommendation_success_sets_fields() -> None:
    user_id = uuid4()
    recommendation = SimpleNamespace(to_user_id=user_id, is_acknowledged=False, acknowledged_at=None)

    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=recommendation))
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = SocialService(session)
    out = await service.acknowledge_recommendation(uuid4(), user_id)

    assert out is recommendation
    assert recommendation.is_acknowledged is True
    assert recommendation.acknowledged_at is not None
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(recommendation)


@pytest.mark.asyncio
async def test_social_create_recommendation_for_shared_group_rejects_self() -> None:
    user_id = uuid4()
    session = MagicMock()
    service = SocialService(session)

    with pytest.raises(ValueError):
        await service.create_recommendation_for_shared_group(
            from_user_id=user_id,
            to_user_id=user_id,
            media_id=uuid4(),
            message="nope",
        )


@pytest.mark.asyncio
async def test_social_create_recommendation_for_shared_group_requires_recipient() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))

    service = SocialService(session)

    with pytest.raises(ValueError):
        await service.create_recommendation_for_shared_group(
            from_user_id=uuid4(),
            to_user_id=uuid4(),
            media_id=uuid4(),
            message="hello",
        )


@pytest.mark.asyncio
async def test_tracking_get_user_statistics_aggregates_counts() -> None:
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=5),
            FakeResult(one_value=2),
            FakeResult(one_value=9),
        ]
    )

    service = TrackingService(session)
    stats = await service.get_user_statistics(uuid4())

    assert stats == {"completed_count": 5, "in_progress_count": 2, "total_count": 9}


@pytest.mark.asyncio
async def test_tracking_get_user_list_entry_returns_none_when_absent() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))

    service = TrackingService(session)
    out = await service.get_user_list_entry(uuid4(), uuid4())

    assert out is None


@pytest.mark.asyncio
async def test_tracking_get_user_list_returns_all_rows() -> None:
    rows = [SimpleNamespace(id=uuid4()), SimpleNamespace(id=uuid4())]
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(all_value=rows))

    service = TrackingService(session)
    out = await service.get_user_list(uuid4(), limit=10, offset=0)

    assert out == rows


@pytest.mark.asyncio
async def test_tracking_update_list_entry_not_found_returns_none() -> None:
    session = MagicMock()
    service = TrackingService(session)
    service.get_user_list_entry = AsyncMock(return_value=None)

    payload = SimpleNamespace(model_dump=lambda **kwargs: {"status": "completed"})
    out = await service.update_list_entry(uuid4(), uuid4(), payload)

    assert out is None


@pytest.mark.asyncio
async def test_tracking_update_list_entry_empty_changes_returns_entry() -> None:
    entry = SimpleNamespace()
    session = MagicMock()
    service = TrackingService(session)
    service.get_user_list_entry = AsyncMock(return_value=entry)

    payload = SimpleNamespace(model_dump=lambda **kwargs: {})
    out = await service.update_list_entry(uuid4(), uuid4(), payload)

    assert out is entry


@pytest.mark.asyncio
async def test_tracking_delete_list_entry_not_found_false() -> None:
    session = MagicMock()
    service = TrackingService(session)
    service.get_user_list_entry = AsyncMock(return_value=None)

    assert await service.delete_list_entry(uuid4(), uuid4()) is False


@pytest.mark.asyncio
async def test_tracking_delete_list_entry_success(monkeypatch) -> None:
    entry = SimpleNamespace(id=uuid4(), user_id=uuid4(), media_id=uuid4(), status="watching", progress=1, score=None)
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    class FakeHistory:
        def __init__(self, **kwargs):
            self.payload = kwargs

    monkeypatch.setattr("src.app.services.tracking_service.ListEntryHistory", FakeHistory)

    service = TrackingService(session)
    service.get_user_list_entry = AsyncMock(return_value=entry)

    assert await service.delete_list_entry(entry.user_id, entry.media_id) is True
    assert entry.deleted_at is not None
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_tracking_replace_custom_list_entries_no_list_returns_none() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))

    service = TrackingService(session)
    payload = SimpleNamespace(entries=[])
    out = await service.replace_custom_list_entries(uuid4(), uuid4(), payload)

    assert out is None


@pytest.mark.asyncio
async def test_tracking_replace_custom_list_entries_success() -> None:
    custom_list = SimpleNamespace(updated_at=None)
    old_rows = [SimpleNamespace(), SimpleNamespace()]
    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=custom_list), FakeResult(all_value=old_rows)])
    session.delete = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    service = TrackingService(session)
    payload = SimpleNamespace(
        entries=[SimpleNamespace(media_id=uuid4(), sort_order=1, note="x"), SimpleNamespace(media_id=uuid4(), sort_order=2, note=None)]
    )

    out = await service.replace_custom_list_entries(uuid4(), uuid4(), payload)
    assert out == 2
    assert session.delete.await_count == 2
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_watch_party_basic_crud_helpers() -> None:
    party = SimpleNamespace(id=uuid4(), deleted_at=None)
    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=party), FakeResult(one_value=party)])
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = WatchPartyService(session)
    got = await service.get_watch_party(party.id)
    assert got is party

    updated = await service.update_watch_party(party.id, {"title": "Updated"})
    assert updated is party
    assert party.title == "Updated"


@pytest.mark.asyncio
async def test_watch_party_delete_not_found_false() -> None:
    session = MagicMock()
    service = WatchPartyService(session)
    service.get_watch_party = AsyncMock(return_value=None)
    assert await service.delete_watch_party(uuid4()) is False


@pytest.mark.asyncio
async def test_watch_party_delete_success() -> None:
    party = SimpleNamespace(deleted_at=None)
    session = MagicMock()
    session.commit = AsyncMock()
    service = WatchPartyService(session)
    service.get_watch_party = AsyncMock(return_value=party)

    assert await service.delete_watch_party(uuid4()) is True
    assert party.deleted_at is not None
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_watch_party_rsvp_create_and_update_paths() -> None:
    user_id = uuid4()
    party_id = uuid4()

    existing = SimpleNamespace(status="pending", responded_at=None)
    created = SimpleNamespace(status="attending")

    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=existing), FakeResult(one_value=None)])
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=[None, None])
    session.add = MagicMock()

    service = WatchPartyService(session)

    out1 = await service.rsvp_to_watch_party(party_id, user_id, "attending")
    assert out1 is existing
    assert existing.status == "attending"

    # second call goes through create branch
    async def refresh_set(obj):
        if hasattr(obj, "status"):
            obj.status = "attending"

    session.refresh = AsyncMock(side_effect=refresh_set)
    out2 = await service.rsvp_to_watch_party(party_id, user_id, "attending")
    assert out2.status == "attending"


@pytest.mark.asyncio
async def test_social_discussion_reply_guard_paths() -> None:
    discussion_id = uuid4()
    user_id = uuid4()
    discussion = SimpleNamespace(id=discussion_id, group_id=uuid4(), deleted_at=None)

    session = MagicMock()
    service = SocialService(session)

    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    with pytest.raises(LookupError):
        await service.create_discussion_reply_for_group_member(user_id=user_id, discussion_id=discussion_id, body="x")

    session.exec = AsyncMock(side_effect=[FakeResult(one_value=discussion), FakeResult(one_value=None)])
    with pytest.raises(PermissionError):
        await service.create_discussion_reply_for_group_member(user_id=user_id, discussion_id=discussion_id, body="x")


@pytest.mark.asyncio
async def test_social_discussion_reply_parent_and_success_paths() -> None:
    discussion_id = uuid4()
    user_id = uuid4()
    discussion = SimpleNamespace(id=discussion_id, group_id=uuid4(), deleted_at=None)
    membership = SimpleNamespace(group_id=discussion.group_id, user_id=user_id)

    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()

    service = SocialService(session)

    # missing parent
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=discussion), FakeResult(one_value=membership), FakeResult(one_value=None)])
    with pytest.raises(LookupError):
        await service.create_discussion_reply_for_group_member(
            user_id=user_id,
            discussion_id=discussion_id,
            body="x",
            parent_reply_id=uuid4(),
        )

    parent = SimpleNamespace(id=uuid4(), discussion_id=discussion_id, deleted_at=None)
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=discussion), FakeResult(one_value=membership), FakeResult(one_value=parent)])
    out = await service.create_discussion_reply_for_group_member(
        user_id=user_id,
        discussion_id=discussion_id,
        body="x",
        parent_reply_id=parent.id,
    )
    assert out is not None


@pytest.mark.asyncio
async def test_social_create_recommendation_shared_group_errors_and_success() -> None:
    from_id = uuid4()
    to_id = uuid4()
    media_id = uuid4()
    recipient = SimpleNamespace(id=to_id, deleted_at=None, is_active=True)

    session = MagicMock()
    service = SocialService(session)

    # no shared group
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=recipient), FakeResult(one_value=None)])
    with pytest.raises(ValueError):
        await service.create_recommendation_for_shared_group(from_id, to_id, media_id, "msg")

    # duplicate recommendation
    existing = SimpleNamespace(id=uuid4())
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=recipient), FakeResult(one_value=uuid4()), FakeResult(one_value=existing)])
    with pytest.raises(ValueError):
        await service.create_recommendation_for_shared_group(from_id, to_id, media_id, "msg")

    # success
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=recipient), FakeResult(one_value=uuid4()), FakeResult(one_value=None)])
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    out = await service.create_recommendation_for_shared_group(from_id, to_id, media_id, "ok")
    assert out is not None
