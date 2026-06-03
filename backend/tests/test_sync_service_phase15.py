"""Tests for SyncService Phase 1.5 de-stubbed methods."""

from __future__ import annotations

from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from sqlmodel import select

from src.app.services.sync_service import SyncService, _parse_anilist_media


# ---------------------------------------------------------------------------
# _parse_anilist_media
# ---------------------------------------------------------------------------

class TestParseAnilistMedia:
    """Verify the AniList response normalisation helper."""

    def test_parses_full_response(self):
        raw = {
            "id": 1,
            "title": {"romaji": "Naruto", "english": "Naruto", "native": "ナルト"},
            "type": "ANIME",
            "format": "TV",
            "status": "FINISHED",
            "description": "A ninja story.",
            "episodes": 220,
            "duration": 23,
            "averageScore": 79,
            "popularity": 1000,
            "trending": 500,
            "season": "FALL",
            "seasonYear": 2002,
            "startDate": {"year": 2002, "month": 10, "day": 3},
            "endDate": {"year": 2007, "month": 2, "day": 8},
            "coverImage": {"large": "https://example.com/large.jpg", "medium": "https://example.com/medium.jpg"},
            "bannerImage": "https://example.com/banner.jpg",
            "isAdult": False,
            "countryOfOrigin": "JP",
            "chapters": None,
            "volumes": None,
            "genres": ["Action", "Adventure"],
            "tags": [{"name": "Ninja", "rank": 90}],
            "studios": {"nodes": [{"name": "Studio Pierrot"}]},
            "relations": {"edges": []},
        }
        parsed = _parse_anilist_media(raw)

        assert parsed["anilist_id"] == 1
        assert parsed["title_romaji"] == "Naruto"
        assert parsed["title_english"] == "Naruto"
        assert parsed["title_native"] == "ナルト"
        assert parsed["media_type"] == "anime"
        assert parsed["format"] == "TV"
        assert parsed["status"] == "finished"
        assert parsed["synopsis"] == "A ninja story."
        assert parsed["episode_count"] == 220
        assert parsed["duration_minutes"] == 23
        assert parsed["average_score"] == 7.9  # 79 / 10
        assert parsed["popularity"] == 1000
        assert parsed["trending"] == 500
        assert parsed["season"] == "fall"
        assert parsed["season_year"] == 2002
        assert parsed["start_date"] == datetime(2002, 10, 3)
        assert parsed["end_date"] == datetime(2007, 2, 8)
        assert parsed["cover_image_large"] == "https://example.com/large.jpg"
        assert parsed["cover_image_medium"] == "https://example.com/medium.jpg"
        assert parsed["banner_image"] == "https://example.com/banner.jpg"
        assert parsed["is_adult"] is False
        assert parsed["country_of_origin"] == "JP"

    def test_parses_minimal_response(self):
        raw = {"id": 42, "title": {"romaji": "Test"}, "type": "MANGA"}
        parsed = _parse_anilist_media(raw)
        assert parsed["anilist_id"] == 42
        assert parsed["title_romaji"] == "Test"
        assert parsed["media_type"] == "manga"
        # Optional fields are None
        assert parsed["title_english"] is None
        assert parsed["format"] is None

    def test_parses_null_dates_gracefully(self):
        raw = {"id": 7, "title": {"romaji": "X"}, "type": "ANIME", "startDate": None, "endDate": None}
        parsed = _parse_anilist_media(raw)
        assert parsed["start_date"] is None
        assert parsed["end_date"] is None

    def test_parses_partial_date_gracefully(self):
        raw = {"id": 8, "title": {"romaji": "Y"}, "type": "ANIME",
               "startDate": {"year": 2020, "month": None, "day": None}}
        parsed = _parse_anilist_media(raw)
        assert parsed["start_date"] is None


# ---------------------------------------------------------------------------
# SyncService.sync_media_from_anilist
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_session():
    """Return a MagicMock that mimics an async DB session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.exec = AsyncMock()
    return session


class FakeSeedRunResult:
    """Simplified SeedRunResult for testing."""
    def __init__(self, processed_items=0, failed_items=0, status="completed"):
        self.processed_items = processed_items
        self.failed_items = failed_items
        self.status = status
        self.source = "test"
        self.errors = []


class TestSyncMediaFromAnilist:
    """Phase 1.5 — de-stubbed sync_media_from_anilist."""

    async def test_happy_path(self, mock_session, monkeypatch):
        """Adapter returns processed items and job is updated."""
        # Monkey-patch at the source module — sync_service imports dynamically inside the function
        class FakeAdapter:
            async def run(self, context):
                return FakeSeedRunResult(processed_items=5, status="completed")

        monkeypatch.setattr(
            "src.app.sync.sources.anilist.AniListSeedAdapter",
            lambda: FakeAdapter(),
        )

        service = SyncService(mock_session)
        # Stub create_sync_job to return a known job
        fake_job = SimpleNamespace(id=uuid4())
        service.create_sync_job = AsyncMock(return_value=fake_job)
        service.update_sync_job = AsyncMock()

        count = await service.sync_media_from_anilist(limit=10)
        assert count == 5
        service.create_sync_job.assert_awaited_once_with("anilist_sync", total_items=10)
        # update_sync_job should have been called with the result
        service.update_sync_job.assert_awaited_once()
        call_kwargs = service.update_sync_job.call_args[0][1]
        assert call_kwargs["processed_items"] == 5
        assert call_kwargs["status"] == "completed"

    async def test_adapter_failure_updates_job(self, mock_session, monkeypatch):
        """When adapter raises, the job is marked as failed and error propagates."""
        class BrokenAdapter:
            async def run(self, context):
                raise RuntimeError("API unavailable")

        monkeypatch.setattr(
            "src.app.sync.sources.anilist.AniListSeedAdapter",
            lambda: BrokenAdapter(),
        )

        fake_job = SimpleNamespace(id=uuid4(), status="running")
        service = SyncService(mock_session)
        service.create_sync_job = AsyncMock(return_value=fake_job)
        service.update_sync_job = AsyncMock()

        with pytest.raises(RuntimeError, match="API unavailable"):
            await service.sync_media_from_anilist(limit=5)

        # update_sync_job should have been called with failure status
        assert service.update_sync_job.await_count == 1
        call_kwargs = service.update_sync_job.call_args[0][1]
        assert call_kwargs["status"] == "failed"
        assert "API unavailable" in call_kwargs["error_log"]


# ---------------------------------------------------------------------------
# SyncService.backfill_missing_metadata
# ---------------------------------------------------------------------------

class TestBackfillMissingMetadata:
    """Phase 1.5 — de-stubbed backfill_missing_metadata."""

    async def test_media_not_found_returns_false(self, mock_session):
        """When MediaEntry is not found, return False."""
        mock_session.exec = AsyncMock(return_value=SimpleNamespace(one_or_none=lambda: None))

        service = SyncService(mock_session)
        result = await service.backfill_missing_metadata(uuid4())
        assert result is False

    async def test_no_external_ids_returns_false(self, mock_session):
        """When MediaExternalIds is not found, return False."""
        fake_media = SimpleNamespace(id=uuid4())
        # First call returns media, second returns None for ext_ids
        mock_session.exec = AsyncMock(
            side_effect=[
                SimpleNamespace(one_or_none=lambda: fake_media),
                SimpleNamespace(one_or_none=lambda: None),
            ]
        )

        service = SyncService(mock_session)
        result = await service.backfill_missing_metadata(fake_media.id)
        assert result is False

    async def test_anilist_backfill_success(self, mock_session, monkeypatch):
        """When anilist_id exists and metadata not synced, call AniListSeedAdapter."""
        media_id = uuid4()
        fake_media = SimpleNamespace(id=media_id, media_type="anime", metadata_synced_at=None)
        fake_ext_ids = SimpleNamespace(media_id=media_id, anilist_id=12345, mangadex_id=None)
        mock_session.exec = AsyncMock(
            side_effect=[
                SimpleNamespace(one_or_none=lambda: fake_media),
                SimpleNamespace(one_or_none=lambda: fake_ext_ids),
            ]
        )

        class FakeAdapter:
            async def run(self, context):
                return FakeSeedRunResult(processed_items=1, status="completed")

        monkeypatch.setattr(
            "src.app.sync.sources.anilist.AniListSeedAdapter",
            lambda: FakeAdapter(),
        )

        service = SyncService(mock_session)
        result = await service.backfill_missing_metadata(media_id)
        assert result is True

    async def test_mangadex_backfill_for_manga(self, mock_session, monkeypatch):
        """When mangadex_id exists and type is manga, call MangaDexSeedAdapter."""
        media_id = uuid4()
        fake_media = SimpleNamespace(id=media_id, media_type="manga", metadata_synced_at=None)
        fake_ext_ids = SimpleNamespace(media_id=media_id, anilist_id=None, mangadex_id="mdex-123")
        mock_session.exec = AsyncMock(
            side_effect=[
                SimpleNamespace(one_or_none=lambda: fake_media),
                SimpleNamespace(one_or_none=lambda: fake_ext_ids),
            ]
        )

        class FakeMangaDexAdapter:
            async def run(self, context):
                return FakeSeedRunResult(processed_items=1, status="completed")

        monkeypatch.setattr(
            "src.app.sync.sources.mangadex.MangaDexSeedAdapter",
            lambda: FakeMangaDexAdapter(),
        )

        service = SyncService(mock_session)
        result = await service.backfill_missing_metadata(media_id)
        assert result is True

    async def test_already_synced_returns_true(self, mock_session):
        """When metadata_synced_at is not None, return True without calling adapters."""
        media_id = uuid4()
        fake_media = SimpleNamespace(id=media_id, media_type="anime", metadata_synced_at=datetime.now(UTC))
        # No anilist_id — metadata is already synced
        fake_ext_ids = SimpleNamespace(media_id=media_id, anilist_id=None, mangadex_id=None)
        mock_session.exec = AsyncMock(
            side_effect=[
                SimpleNamespace(one_or_none=lambda: fake_media),
                SimpleNamespace(one_or_none=lambda: fake_ext_ids),
            ]
        )

        service = SyncService(mock_session)
        result = await service.backfill_missing_metadata(media_id)
        assert result is True


# ---------------------------------------------------------------------------
# SyncService.update_or_create_media_from_anilist
# ---------------------------------------------------------------------------

class TestUpdateOrCreateMediaFromAnilist:
    """Phase 1.5 — de-stubbed update_or_create_media_from_anilist."""

    async def test_create_new_entry(self, mock_session, monkeypatch):
        """When no existing external_ids row, create MediaEntry + MediaExternalIds."""
        mock_session.exec = AsyncMock(return_value=SimpleNamespace(one_or_none=lambda: None))
        mock_session.flush = AsyncMock()

        service = SyncService(mock_session)

        raw_data = {
            "id": 999,
            "title": {"romaji": "New Anime", "english": "New Anime"},
            "type": "ANIME",
            "format": "TV",
            "status": "RELEASING",
            "averageScore": 85,
            "popularity": 500,
        }

        entry = await service.update_or_create_media_from_anilist(raw_data)

        assert entry.title_romaji == "New Anime"
        assert entry.media_type == "anime"
        assert entry.format == "TV"
        assert entry.average_score == 8.5
        assert entry.metadata_synced_at is not None

        # Should have called session.add for both MediaEntry and MediaExternalIds
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_awaited_once()

    async def test_update_existing_entry(self, mock_session):
        """When external_ids row exists, update the associated MediaEntry."""
        media_id = uuid4()

        # Use SimpleNamespace for both objects — allows free attribute setting/reading
        existing_media = SimpleNamespace(
            id=media_id,
            title_romaji="Old Title",
            media_type="anime",
            format=None,
            status=None,
            synopsis=None,
            cover_image_large=None,
            cover_image_medium=None,
            banner_image=None,
            episode_count=None,
            chapter_count=None,
            volume_count=None,
            duration_minutes=None,
            average_score=None,
            popularity=None,
            trending=None,
            season=None,
            season_year=None,
            start_date=None,
            end_date=None,
            is_adult=False,
            country_of_origin=None,
            metadata_synced_at=None,
            updated_at=datetime(2020, 1, 1),
        )

        existing_ext_ids = SimpleNamespace(
            anilist_id=888,
            media_id=media_id,
        )

        # exec returns ext_ids first (for lookup), then media on second call
        mock_session.exec = AsyncMock(
            side_effect=[
                SimpleNamespace(one_or_none=lambda: existing_ext_ids),  # lookup by anilist_id
                SimpleNamespace(one_or_none=lambda: existing_media),    # lookup media by id
            ]
        )

        service = SyncService(mock_session)

        raw_data = {
            "id": 888,
            "title": {"romaji": "Updated Title", "english": "Updated"},
            "type": "ANIME",
            "format": "TV",
            "averageScore": 90,
        }

        entry = await service.update_or_create_media_from_anilist(raw_data)

        assert entry.title_romaji == "Updated Title"
        assert entry.average_score == 9.0
        assert entry.updated_at is not None
        assert entry.metadata_synced_at is not None

    async def test_missing_anilist_id_raises(self, mock_session):
        """When raw data has no 'id' field, raise ValueError."""
        service = SyncService(mock_session)
        with pytest.raises(ValueError, match="missing 'id' field"):
            await service.update_or_create_media_from_anilist({"title": {"romaji": "No ID"}})

    async def test_orphaned_ext_ids_raises(self, mock_session):
        """When ext_ids references a media that doesn't exist, raise ValueError."""
        existing_ext_ids = MagicMock()
        existing_ext_ids.anilist_id = 777
        existing_ext_ids.media_id = uuid4()

        mock_session.exec = AsyncMock(
            side_effect=[
                SimpleNamespace(one_or_none=lambda: existing_ext_ids),  # lookup by anilist_id
                SimpleNamespace(one_or_none=lambda: None),              # media not found
            ]
        )

        service = SyncService(mock_session)
        with pytest.raises(ValueError, match="MediaEntry not found"):
            await service.update_or_create_media_from_anilist({
                "id": 777,
                "title": {"romaji": "Orphan"},
                "type": "ANIME",
            })
