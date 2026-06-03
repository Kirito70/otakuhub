from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from src.app.services.social_service import SocialService


class FakeResult:
    def __init__(self, *, all_value=None, one_value=None):
        self._all_value = [] if all_value is None else all_value
        self._one_value = one_value

    def all(self):
        return self._all_value

    def one_or_none(self):
        return self._one_value


@pytest.mark.asyncio
async def test_social_read_queries_return_rows() -> None:
    row = SimpleNamespace(id=uuid4())
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(all_value=[row]),  # get_user_recommendations
            FakeResult(all_value=[row]),  # inbox
            FakeResult(one_value=3),      # count inbox
            FakeResult(all_value=[row]),  # group feed
            FakeResult(one_value=2),      # count group feed
            FakeResult(all_value=[row]),  # sent recs
            FakeResult(all_value=[row]),  # discussions
            FakeResult(all_value=[row]),  # discussions for user/media
            FakeResult(one_value=4),      # count discussions for user/media
            FakeResult(all_value=[row]),  # discussion replies
            FakeResult(all_value=[row]),  # notifications
        ]
    )

    svc = SocialService(session)
    user_id = uuid4()
    media_id = uuid4()

    assert await svc.get_user_recommendations(user_id, limit=5) == [row]
    assert await svc.get_user_recommendations_inbox(user_id, limit=5, offset=0, include_acknowledged=False) == [row]
    assert await svc.count_user_recommendations_inbox(user_id, include_acknowledged=False) == 3
    assert await svc.get_group_activity_feed(user_id, limit=10, offset=0) == [row]
    assert await svc.count_group_activity_feed(user_id) == 2
    assert await svc.get_user_sent_recommendations(user_id, limit=3) == [row]
    assert await svc.get_discussions(media_id, group_id=None, limit=5, offset=0) == [row]
    assert await svc.get_discussions_for_user_media(user_id=user_id, media_id=media_id, group_id=None, limit=5, offset=0) == [row]
    assert await svc.count_discussions_for_user_media(user_id=user_id, media_id=media_id, group_id=None) == 4
    assert await svc.get_discussion_replies(uuid4(), limit=20) == [row]
    assert await svc.get_user_notifications(user_id, limit=5, is_read=False) == [row]


@pytest.mark.asyncio
async def test_social_create_recommendation_simple_success() -> None:
    rec = SimpleNamespace(id=uuid4())
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock(side_effect=lambda obj: None)

    svc = SocialService(session)
    out = await svc.create_recommendation(uuid4(), uuid4(), uuid4(), "msg")

    assert out is not None
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_social_create_recommendation_for_shared_group_branches() -> None:
    from_user = uuid4()
    to_user = uuid4()
    media_id = uuid4()

    # recipient missing
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc = SocialService(session)
    with pytest.raises(ValueError):
        await svc.create_recommendation_for_shared_group(from_user, to_user, media_id, "m")

    # no shared group
    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=SimpleNamespace(id=to_user)), FakeResult(one_value=None)])
    svc = SocialService(session)
    with pytest.raises(ValueError):
        await svc.create_recommendation_for_shared_group(from_user, to_user, media_id, "m")

    # duplicate
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=SimpleNamespace(id=to_user)),
            FakeResult(one_value=uuid4()),
            FakeResult(one_value=SimpleNamespace(id=uuid4())),
        ]
    )
    svc = SocialService(session)
    with pytest.raises(ValueError):
        await svc.create_recommendation_for_shared_group(from_user, to_user, media_id, "m")

    # success
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=SimpleNamespace(id=to_user)),
            FakeResult(one_value=uuid4()),
            FakeResult(one_value=None),
        ]
    )
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = SocialService(session)
    out = await svc.create_recommendation_for_shared_group(from_user, to_user, media_id, "m")
    assert out is not None
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_social_discussion_create_and_group_member_paths() -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = SocialService(session)
    out = await svc.create_discussion(uuid4(), uuid4(), uuid4(), "title", "body")
    assert out is not None

    # non-member
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc = SocialService(session)
    with pytest.raises(PermissionError):
        await svc.create_discussion_for_group_member(uuid4(), uuid4(), uuid4(), "t", "b")

    # integrity failure
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=SimpleNamespace(id=uuid4())))
    session.add = MagicMock()
    session.commit = AsyncMock(side_effect=IntegrityError("stmt", "params", Exception("x")))
    session.rollback = AsyncMock()
    svc = SocialService(session)
    with pytest.raises(ValueError):
        await svc.create_discussion_for_group_member(uuid4(), uuid4(), uuid4(), "t", "b")

    # success
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=SimpleNamespace(id=uuid4())))
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = SocialService(session)
    out = await svc.create_discussion_for_group_member(uuid4(), uuid4(), uuid4(), "t", "b")
    assert out is not None


@pytest.mark.asyncio
async def test_social_reply_paths() -> None:
    # plain create
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = SocialService(session)
    out = await svc.create_discussion_reply(uuid4(), uuid4(), body="b")
    assert out is not None

    # missing discussion
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc = SocialService(session)
    with pytest.raises(LookupError):
        await svc.create_discussion_reply_for_group_member(user_id=uuid4(), discussion_id=uuid4(), body="b")

    # missing membership
    discussion = SimpleNamespace(id=uuid4(), group_id=uuid4(), deleted_at=None)
    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=discussion), FakeResult(one_value=None)])
    svc = SocialService(session)
    with pytest.raises(PermissionError):
        await svc.create_discussion_reply_for_group_member(user_id=uuid4(), discussion_id=discussion.id, body="b")

    # missing parent reply
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=discussion),
            FakeResult(one_value=SimpleNamespace(id=uuid4())),
            FakeResult(one_value=None),
        ]
    )
    svc = SocialService(session)
    with pytest.raises(LookupError):
        await svc.create_discussion_reply_for_group_member(
            user_id=uuid4(),
            discussion_id=discussion.id,
            body="b",
            parent_reply_id=uuid4(),
        )

    # success
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=discussion),
            FakeResult(one_value=SimpleNamespace(id=uuid4())),
            FakeResult(one_value=SimpleNamespace(id=uuid4())),
        ]
    )
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = SocialService(session)
    out = await svc.create_discussion_reply_for_group_member(
        user_id=uuid4(), discussion_id=discussion.id, body="b", parent_reply_id=uuid4()
    )
    assert out is not None


@pytest.mark.asyncio
async def test_social_notifications_and_preferences_paths() -> None:
    uid = uuid4()

    # mark read false then true
    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=None), FakeResult(one_value=SimpleNamespace(user_id=uid, is_read=False, read_at=None))])
    session.commit = AsyncMock()
    svc = SocialService(session)
    assert await svc.mark_notification_as_read(uuid4(), uid) is False
    assert await svc.mark_notification_as_read(uuid4(), uid) is True

    # create notification - verify it succeeds now that UUID defaults are fixed
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = SocialService(session)
    result = await svc.create_notification(uid, "system", "t", "b")
    assert result is not None
    assert result.user_id == uid
    assert result.type == "system"

    # get preferences existing and missing
    pref = SimpleNamespace(user_id=uid)
    session = MagicMock()
    session.exec = AsyncMock(side_effect=[FakeResult(one_value=pref), FakeResult(one_value=None)])
    session.add = MagicMock()
    session.commit = AsyncMock()
    svc = SocialService(session)
    assert await svc.get_notification_preferences(uid) is pref
    out = await svc.get_notification_preferences(uid)
    assert out is not None

    # update prefs existing
    pref2 = SimpleNamespace(user_id=uid, new_episode=True)
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=pref2))
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    svc = SocialService(session)
    out = await svc.update_notification_preferences(uid, {"new_episode": False})
    assert out.new_episode is False


@pytest.mark.asyncio
async def test_social_get_user_watch_parties_returns_typed_rows() -> None:
    now = datetime.utcnow() + timedelta(hours=1)
    party = SimpleNamespace(
        id=uuid4(),
        host_user_id=uuid4(),
        media_id=uuid4(),
        group_id=uuid4(),
        title="Friday Party",
        scheduled_at=now,
        status="scheduled",
        stream_url="https://example.com/stream",
        sync_url="https://example.com/sync",
    )

    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(all_value=[(party, "Romaji Title", "English Title")]))

    svc = SocialService(session)
    out = await svc.get_user_watch_parties(uuid4(), limit=5)

    assert len(out) == 1
    assert out[0]["id"] == str(party.id)
    assert out[0]["media_title"] == "English Title"
    assert out[0]["stream_url"] == "https://example.com/stream"
