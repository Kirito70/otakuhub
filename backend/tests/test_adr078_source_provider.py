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
from src.app.external.megaplay_client import MegaPlayAvailabilityClient, MegaPlayEmbedResolver
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

    client = AnikotoClient(base_url="https://anikoto.test", max_retries=0, http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))

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

    # safe_embed_url (full URL validation)
    assert MegaPlayEmbedResolver.safe_embed_url("https://megaplay.buzz/stream/s-2/136197/dub") is True
    assert MegaPlayEmbedResolver.safe_embed_url("https://evil.example/stream/s-2/136197/dub") is False
    assert MegaPlayEmbedResolver.safe_embed_url("https://megaplay.buzz/hls/playlist.m3u8") is False
    assert MegaPlayEmbedResolver.safe_embed_url("") is False
    assert MegaPlayEmbedResolver.safe_embed_url("not-a-url") is False

    # MAL / AniList direct resolution URLs
    assert MegaPlayEmbedResolver.build_mal_url(52991, 1, "sub") == "https://megaplay.buzz/stream/mal/52991/1/sub"
    assert MegaPlayEmbedResolver.build_anilist_url(154587, 5, "dub") == "https://megaplay.buzz/stream/ani/154587/5/dub"


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
    # Full payload and titles stored
    assert mapping.source_payload is not None
    assert mapping.source_payload["title"] == "Frieren"
    assert mapping.source_payload["anilist_id"] == 154587
    assert mapping.source_titles is not None
    assert mapping.source_titles["romaji"] == "Frieren"
    assert mapping.details_synced_at is not None
    episode = (await db_session.exec(select(MediaSourceEpisode).where(MediaSourceEpisode.source_episode_id == "frieren-1"))).one()
    assert episode.embed_url == "https://megaplay.buzz/e/frieren-1"
    # Episode payload and streaming options stored
    assert episode.source_payload is not None
    assert episode.source_payload["episode_embed_id"] == "frieren-1"
    assert episode.details_synced_at is not None

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
    assert episode.embed_url == "https://megaplay.buzz/stream/s-2/136197/dub"

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


@pytest.mark.asyncio
async def test_anikoto_service_creates_minimal_media_entry_from_provider_ids(db_session):
    service = AnikotoSyncService(db_session)
    media_id, episode_count = await service.upsert_series(
        {
            "id": "new-provider-title",
            "title": "New Provider Title",
            "ani_id": "123456",
            "mal_id": "654321",
            "status": "Finished Airing",
            "year": 2026,
            "episodes": [{"episode_embed_id": "new-1", "number": 1}],
        }
    )

    assert media_id is not None
    assert episode_count == 1
    media = (await db_session.exec(select(MediaEntry).where(MediaEntry.id == media_id))).one()
    ext = (await db_session.exec(select(MediaExternalIds).where(MediaExternalIds.media_id == media_id))).one()
    mapping = (await db_session.exec(select(MediaSourceMapping).where(MediaSourceMapping.source_media_id == "new-provider-title"))).one()
    episode = (await db_session.exec(select(MediaSourceEpisode).where(MediaSourceEpisode.source_episode_id == "new-1"))).one()

    assert media.title_romaji == "New Provider Title"
    assert ext.anilist_id == 123456
    assert ext.mal_id == 654321
    assert mapping.media_id == media.id
    assert mapping.mapping_status == "matched"

    await db_session.delete(episode)
    await db_session.delete(mapping)
    await db_session.delete(ext)
    await db_session.delete(media)
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


def test_anikoto_client_adapts_rate_limit_from_headers():
    """X-RateLimit-* headers dynamically tighten the token bucket."""
    client = AnikotoClient(max_retries=0)
    # Default bucket is 55
    assert client.rate_limiter.max_requests == 55

    # Simulate a response saying only 3 tokens remain → bucket tightens
    resp = httpx.Response(200, headers={"X-RateLimit-Remaining": "3", "X-RateLimit-Reset": "30"})
    client._adapt_rate_limit_from_headers(resp)
    # remaining - safety = 3 - 2 = 1, floor at 2
    assert client.rate_limiter.max_requests == 2

    # No headers → no change
    resp2 = httpx.Response(200, headers={})
    client._adapt_rate_limit_from_headers(resp2)
    assert client.rate_limiter.max_requests == 2


@pytest.mark.asyncio
async def test_anikoto_adapter_handles_429_gracefully(db_session):
    """Verify the adapter continues after a 429 on list fetch."""
    from src.app.sync.sources.anikoto import AnikotoSourceAdapter
    from src.app.sync.types import SeedExecutionContext

    call_count = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            # First call: 429 to test backoff
            return httpx.Response(429, headers={"Retry-After": "1"}, json={})
        # Second call succeeds
        return httpx.Response(200, json={"data": [{"id": "ok-1", "title": "OK Title"}]})

    client = AnikotoClient(
        max_retries=0,
        base_url="https://anikoto.test",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    adapter = AnikotoSourceAdapter(mode="full", client=client)
    ctx = SeedExecutionContext(source="test", job_id="test-429", per_page=5, max_pages=1, refresh_details=False, dry_run=True)
    result = await adapter.run(ctx)

    assert result.processed_items == 1
    assert result.failed_items == 0


@pytest.mark.asyncio
async def test_megaplay_availability_client_reports_unavailable_for_bad_url():
    """Availability client returns False for non-resolving embed URLs."""
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(410, json={})  # Gone

    client = MegaPlayAvailabilityClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    result = await client.check_url("https://megaplay.buzz/stream/s-2/136197/dub")
    assert result is False


@pytest.mark.asyncio
async def test_megaplay_availability_client_reports_available_for_good_url():
    """Availability client returns True when embed URL resolves."""
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    client = MegaPlayAvailabilityClient(http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    result = await client.check_url("https://megaplay.buzz/stream/s-2/136197/sub")
    assert result is True


@pytest.mark.asyncio
async def test_megaplay_availability_client_rejects_unsafe_url():
    """Availability client returns False for URLs that fail safe_embed_url validation."""
    client = MegaPlayAvailabilityClient()
    assert await client.check_url("https://evil.example/stream/s-2/136197/dub") is False
    assert await client.check_url("") is False
    assert await client.check_url("not-a-url") is False


def test_admin_megaplay_verify_endpoint(monkeypatch):
    """Admin megaplay/verify endpoint enqueues a Celery task."""
    class _FakeTask:
        def delay(self, **kwargs):
            self.kwargs = kwargs
            return SimpleNamespace(id="verify-123")

    verify_task = _FakeTask()
    monkeypatch.setattr("src.app.routes.admin.megaplay_verify_availability_task", verify_task)

    with TestClient(app) as client:
        login = client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
        assert login.status_code == 200, login.text
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        response = client.post("/api/v1/admin/sync/providers/megaplay/verify", headers=headers)

    assert response.status_code == 202, response.text
    assert response.json()["job_type"] == "megaplay_verify_availability"


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
