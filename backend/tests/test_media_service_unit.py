from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.app.models.enums import MediaStatus, MediaType
from src.app.services.media_service import MediaService


class FakeResult:
    def __init__(self, *, all_value=None, one_value=None):
        self._all_value = [] if all_value is None else all_value
        self._one_value = one_value

    def all(self):
        return self._all_value

    def one_or_none(self):
        return self._one_value


@pytest.mark.asyncio
async def test_media_service_repository_delegations(monkeypatch) -> None:
    session = MagicMock()
    svc = MediaService(session)

    repo = MagicMock()
    media = SimpleNamespace(id=uuid4())
    repo.get_by_id = AsyncMock(return_value=media)
    repo.search_media = AsyncMock(return_value=[media])
    repo.get_popular_media = AsyncMock(return_value=[media])
    repo.get_trending_media = AsyncMock(return_value=[media])
    repo.create = AsyncMock(return_value=media)
    repo.update = AsyncMock(return_value=media)
    repo.get_by_external_id = AsyncMock(return_value=media)
    repo.get_by_title = AsyncMock(return_value=media)
    repo.get_by_status = AsyncMock(return_value=[media])
    svc._media_repository = repo

    assert await svc.get_media_by_id(media.id) is media
    assert await svc.search_media(query="naruto") == [media]
    assert await svc.get_popular_media(media_type="anime", limit=5) == [media]
    assert await svc.get_trending_media(media_type="anime", limit=5) == [media]
    assert await svc.create_media({"title_romaji": "x"}) is media
    assert await svc.update_media(media.id, {"title_romaji": "y"}) is media
    assert await svc.get_by_external_id(1, "anilist") is media
    assert await svc.get_by_title("x") is media
    assert await svc.get_by_status("releasing", limit=5) == [media]
    assert await svc.get_related_media(media.id) == []


@pytest.mark.asyncio
async def test_media_service_get_media_detail_none_when_missing() -> None:
    svc = MediaService(MagicMock())
    svc.get_media_by_id = AsyncMock(return_value=None)

    assert await svc.get_media_detail(uuid4()) is None


@pytest.mark.asyncio
async def test_media_service_get_media_detail_success() -> None:
    media_id = uuid4()
    now = datetime.utcnow()
    media = SimpleNamespace(
        id=media_id,
        title_romaji="Title",
        title_english="Title EN",
        title_native="タイトル",
        media_type=MediaType.anime,
        format=None,
        status=MediaStatus.finished,
        synopsis="synopsis",
        cover_image_large=None,
        cover_image_medium=None,
        banner_image=None,
        episode_count=12,
        chapter_count=None,
        volume_count=None,
        duration_minutes=24,
        average_score=8.1,
        popularity=100,
        trending=50,
        season=None,
        season_year=2024,
        start_date=None,
        end_date=None,
        is_adult=False,
        country_of_origin="JP",
        created_at=now,
        updated_at=now,
    )

    ext = SimpleNamespace(anilist_id=123)
    genre = SimpleNamespace(name="Action")
    studio = SimpleNamespace(name="Studio")
    tag = SimpleNamespace(name="Tag")

    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=ext),
            FakeResult(all_value=[genre]),
            FakeResult(all_value=[studio]),
            FakeResult(all_value=[tag]),
        ]
    )

    svc = MediaService(session)
    svc.get_media_by_id = AsyncMock(return_value=media)
    detail = await svc.get_media_detail(media_id)

    assert detail is not None
    assert detail.id == media_id
    assert detail.external_ids is ext
    assert len(detail.genres) == 1
    assert len(detail.studios) == 1
    assert len(detail.tags) == 1


@pytest.mark.asyncio
async def test_media_service_delete_paths() -> None:
    session = MagicMock()
    session.commit = AsyncMock()
    svc = MediaService(session)

    svc.get_media_by_id = AsyncMock(side_effect=[None, SimpleNamespace(deleted_at=None)])
    assert await svc.delete_media(uuid4()) is False
    assert await svc.delete_media(uuid4()) is True
    session.commit.assert_awaited_once()
