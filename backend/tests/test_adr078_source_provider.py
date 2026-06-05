from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from src.app.external.anikoto_client import AnikotoClient, AnikotoForbiddenError, AnikotoRateLimitError
from src.app.external.megaplay_client import MegaPlayEmbedResolver
from src.app.main import app
from src.app.models.media_entry import MediaEntry
from src.app.models.media_external_ids import MediaExternalIds
from src.app.models.media_source_episode import MediaSourceEpisode
from src.app.models.media_source_mapping import MediaSourceMapping
from src.app.repositories.source_provider_repository import SourceEpisodeRepository, SourceMappingRepository
from src.app.schemas.source_provider import SourceEpisodeUpsert, SourceMappingUpsert
from src.app.services.anikoto_sync_service import AnikotoSyncService, normalize_title
from src.app.sync.factory import build_seed_orchestrator
from src.app.workers import sync_tasks
from tests.helpers import ADMIN_PASSWORD, ADMIN_USERNAME


@pytest.mark.asyncio
async def test_source_mapping_and_episode_upserts_are_idempotent(db_session):
    mapping_repo = SourceMappingRepository(db_session)
    episode_repo = SourceEpisodeRepository(db_session)

    mapping = await mapping_repo.upsert(
        SourceMappingUpsert(source="anikoto", source_media_id="series-1", source_title="Naruto", mapping_status="unmatched", match_confidence=Decimal("0.00"))
    )
    updated = await mapping_repo.upsert(
        SourceMappingUpsert(source="anikoto", source_media_id="series-1", source_title="Naruto Shippuden", mapping_status="matched", match_confidence=Decimal("92.00"))
    )

    assert updated.id == mapping.id
    assert updated.source_title == "Naruto Shippuden"
    assert updated.mapping_status == "matched"

    episode = await episode_repo.upsert(
        SourceEpisodeUpsert(mapping_id=mapping.id, source="anikoto", source_episode_id="ep-1", episode_number=Decimal("1"), language="sub")
    )
    episode_updated = await episode_repo.upsert(
        SourceEpisodeUpsert(mapping_id=mapping.id, source="anikoto", source_episode_id="ep-1", episode_number=Decimal("1"), language="sub", title="Episode 1")
    )

    assert episode_updated.id == episode.id
    assert episode_updated.title == "Episode 1"

    await db_session.delete(episode_updated)
    await db_session.delete(updated)
    await db_session.commit()


@pytest.mark.asyncio
async def test_anikoto_client_uses_documented_paths_and_handles_errors():
    seen: list[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        if request.url.path == "/recent-anime":
            return httpx.Response(200, json={"data": [{"id": "s1"}]})
        if request.url.path == "/series/s1":
            return httpx.Response(200, json={"id": "s1", "episodes": []})
        if request.url.path == "/series/limited":
            return httpx.Response(429, headers={"Retry-After": "12"}, json={})
        return httpx.Response(403, json={})

    client = AnikotoClient(base_url="https://anikoto.test", http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    assert await client.get_recent_anime(page=2, per_page=10) == {"data": [{"id": "s1"}]}
    assert (await client.get_series("s1"))["id"] == "s1"
    with pytest.raises(AnikotoRateLimitError) as rate_limit:
        await client.get_series("limited")
    assert rate_limit.value.retry_after == 12
    with pytest.raises(AnikotoForbiddenError):
        await client.get_series("forbidden")
    assert "/recent-anime?page=2&per_page=10" in seen[0]


def test_megaplay_embed_resolver_builds_safe_paths_only():
    assert MegaPlayEmbedResolver.build_episode_path("136197", "dub") == "/stream/s-2/136197/dub"
    assert MegaPlayEmbedResolver.build_episode_url("136197", "sub") == "https://megaplay.buzz/stream/s-2/136197/sub"
    assert MegaPlayEmbedResolver.safe_embed_path("https://megaplay.buzz/stream/s-2/136197/dub") == "/stream/s-2/136197/dub"
    assert MegaPlayEmbedResolver.safe_embed_path("https://evil.example/stream/s-2/136197/dub") is None
    assert MegaPlayEmbedResolver.safe_embed_path("https://megaplay.buzz/hls/playlist.m3u8") is None


def test_seed_orchestrator_build_is_lazy_for_provider_sources(monkeypatch):
    def _raise_if_eager(*args, **kwargs):
        raise AssertionError("anime-offline adapter should not initialize during factory construction")

    monkeypatch.setattr("src.app.sync.factory.AnimeOfflineSeedAdapter", _raise_if_eager)
    orchestrator = build_seed_orchestrator(MagicMock())

    assert "anikoto_full_catalog" in orchestrator.adapters


@pytest.mark.asyncio
async def test_anikoto_service_matches_anilist_then_stores_episodes(db_session):
    media = MediaEntry(id=uuid4(), title_romaji="Frieren", media_type="anime", status="finished", season_year=2023)
    db_session.add(media)
    db_session.add(MediaExternalIds(media_id=media.id, anilist_id=154587, mal_id=52991))
    await db_session.commit()

    service = AnikotoSyncService(db_session)
    media_id, episode_count = await service.upsert_series(
        {
            "id": "frieren-anikoto",
            "title": "Frieren",
            "anilist_id": 154587,
            "episodes": [{"episode_embed_id": "frieren-1", "episode_number": 1, "language": "sub", "embed_url": "https://megaplay.buzz/e/frieren-1"}],
        }
    )

    assert media_id == media.id
    assert episode_count == 1
    mapping = (await db_session.exec(select(MediaSourceMapping).where(MediaSourceMapping.source_media_id == "frieren-anikoto"))).one()
    assert mapping.media_id == media.id
    assert mapping.mapping_status == "matched"
    episode = (await db_session.exec(select(MediaSourceEpisode).where(MediaSourceEpisode.source_episode_id == "frieren-1"))).one()
    assert episode.embed_path == "/e/frieren-1"

    ext = (await db_session.exec(select(MediaExternalIds).where(MediaExternalIds.media_id == media.id))).one()
    await db_session.delete(episode)
    await db_session.delete(mapping)
    await db_session.delete(ext)
    await db_session.delete(media)
    await db_session.commit()


@pytest.mark.asyncio
async def test_anikoto_service_builds_megaplay_path_from_episode_embed_id(db_session):
    service = AnikotoSyncService(db_session)
    _, episode_count = await service.upsert_series(
        {
            "id": "megaplay-only",
            "title": "MegaPlay Only",
            "episodes": [{"episode_embed_id": "136197", "episode_number": 1, "language": "dub"}],
        }
    )

    assert episode_count == 1
    episode = (await db_session.exec(select(MediaSourceEpisode).where(MediaSourceEpisode.source_episode_id == "136197"))).one()
    mapping = (await db_session.exec(select(MediaSourceMapping).where(MediaSourceMapping.source_media_id == "megaplay-only"))).one()
    assert episode.embed_path == "/stream/s-2/136197/dub"

    await db_session.delete(episode)
    await db_session.delete(mapping)
    await db_session.commit()


@pytest.mark.asyncio
async def test_anikoto_service_unmatched_for_uncertain_title(db_session):
    service = AnikotoSyncService(db_session)
    media_id, _ = await service.upsert_series({"id": "unknown", "title": "Some Unmatched Provider Title", "year": 1999, "episodes": []})

    assert media_id is None
    mapping = (await db_session.exec(select(MediaSourceMapping).where(MediaSourceMapping.source_media_id == "unknown"))).one()
    assert mapping.media_id is None
    assert mapping.mapping_status == "unmatched"
    assert normalize_title(mapping.source_title) == "some unmatched provider title"

    await db_session.delete(mapping)
    await db_session.commit()


def test_daily_refresh_compose_includes_anikoto_only_when_enabled(monkeypatch):
    calls: list[str] = []

    class _FakeTask:
        def __init__(self, label: str):
            self.label = label

        def s(self, **kwargs):
            calls.append(self.label)
            return SimpleNamespace(label=self.label, kwargs=kwargs)

    class _FakeChain:
        def apply_async(self):
            return SimpleNamespace(id="daily-1")

    monkeypatch.setattr(sync_tasks, "backfill_anilist_task", _FakeTask("anilist"))
    monkeypatch.setattr(sync_tasks, "mangadex_detail_task", _FakeTask("mangadex"))
    monkeypatch.setattr(sync_tasks, "anikoto_recent_refresh_task", _FakeTask("anikoto"))
    monkeypatch.setattr(sync_tasks, "chain", lambda *signatures: _FakeChain())

    monkeypatch.setattr(sync_tasks.settings, "anikoto_sync_enabled", False)
    sync_tasks.daily_refresh_compose_task()
    assert calls == ["anilist", "mangadex"]

    calls.clear()
    monkeypatch.setattr(sync_tasks.settings, "anikoto_sync_enabled", True)
    sync_tasks.daily_refresh_compose_task()
    assert calls == ["anilist", "mangadex", "anikoto"]


def test_admin_anikoto_enqueue_endpoints(monkeypatch):
    class _FakeTask:
        def delay(self, **kwargs):
            self.kwargs = kwargs
            return SimpleNamespace(id="task-123")

    full_task = _FakeTask()
    recent_task = _FakeTask()
    monkeypatch.setattr("src.app.routes.admin.anikoto_full_catalog_task", full_task)
    monkeypatch.setattr("src.app.routes.admin.anikoto_recent_refresh_task", recent_task)

    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        assert login.status_code == 200, login.text
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        full = client.post("/api/v1/admin/sync/providers/anikoto/full", json={"per_page": 10, "max_pages": 2}, headers=headers)
        recent = client.post("/api/v1/admin/sync/providers/anikoto/recent", json={"per_page": 5, "max_pages": 1}, headers=headers)
        megaplay = client.post("/api/v1/admin/sync/providers/megaplay/recent", json={"per_page": 6, "max_pages": 1}, headers=headers)

    assert full.status_code == 202, full.text
    assert full.json()["job_type"] == "anikoto_full_catalog"
    assert full_task.kwargs["per_page"] == 10
    assert recent.status_code == 202, recent.text
    assert recent.json()["job_type"] == "anikoto_recent_refresh"
    assert megaplay.status_code == 202, megaplay.text
    assert megaplay.json()["job_type"] == "anikoto_recent_refresh"
    assert recent_task.kwargs["per_page"] == 6
