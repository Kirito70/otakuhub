from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlmodel import SQLModel

from src.app.models.sync_job import SyncJob
from src.app.models.user import User
from src.app.repositories.base_repository import BaseRepository
from src.app.repositories.query_builder import QueryBuilder, QueryBuilderPattern
from src.app.services.sync_service import SyncService


@pytest.fixture(autouse=True)
def stub_sync_clients(monkeypatch):
    # AniListSeedAdapter and MangaDexSeedAdapter are now lazily imported inside
    # SyncService methods. We stub them at the source module so lazy imports
    # in sync_media_from_anilist() and backfill_missing_metadata() get mocks.
    from unittest.mock import AsyncMock

    mock_adapter = AsyncMock()
    mock_adapter.run = AsyncMock(
        return_value=SimpleNamespace(processed_items=0, failed_items=0, status="completed")
    )
    monkeypatch.setattr(
        "src.app.sync.sources.anilist.AniListSeedAdapter",
        lambda: mock_adapter,
    )
    monkeypatch.setattr(
        "src.app.sync.sources.mangadex.MangaDexSeedAdapter",
        lambda: mock_adapter,
    )



class FakeResult:
    def __init__(self, *, all_value=None, one_value=None):
        self._all_value = [] if all_value is None else all_value
        self._one_value = one_value

    def all(self):
        return self._all_value

    def one_or_none(self):
        return self._one_value


@pytest.mark.asyncio
async def test_query_builder_all_first_count_exists_paths() -> None:
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(all_value=[1, 2]),
            FakeResult(one_value=1),
            FakeResult(one_value=7),
            FakeResult(one_value=True),
        ]
    )

    qb = QueryBuilder(User, session)
    qb = qb.filter(User.username == "demo").desc(User.created_at).limit(5).offset(1)

    all_rows = await qb.all()
    first_row = await qb.first()
    total = await qb.count()
    exists = await qb.exists()

    assert all_rows == [1, 2]
    assert first_row == 1
    assert total == 7
    assert exists is True
    assert session.exec.await_count == 4


@pytest.mark.asyncio
async def test_query_builder_or_join_group_having_clone_and_with_deleted() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(all_value=[]))

    base = QueryBuilder(User, session).where(User.is_active == True)  # noqa: E712
    chained = (
        base.or_(User.is_admin == True)  # noqa: E712
        .join(User, isouter=True)
        .group_by(User.id)
        .having(User.id.is_not(None))
        .asc(User.username)
    )

    clone = chained.clone()
    with_deleted = chained.with_deleted()

    await clone.all()
    await with_deleted.all()

    assert clone is not chained
    assert with_deleted is not chained
    assert with_deleted._include_deleted is True


def test_query_builder_pattern_build_returns_query_builder() -> None:
    session = MagicMock()
    qb = QueryBuilderPattern.build(User, session)
    assert isinstance(qb, QueryBuilder)


@pytest.mark.asyncio
async def test_base_repository_create_update_delete_and_count() -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    repo = BaseRepository(User, session)

    created = await repo.create(
        {
            "username": "repo_user",
            "email": "repo_user@example.com",
            "password_hash": "hashed",
        }
    )
    assert created.username == "repo_user"

    repo.get_by_id = AsyncMock(return_value=created)
    updated = await repo.update(created.id, {"display_name": "Repo User"})
    assert updated is created
    assert created.display_name == "Repo User"

    deleted = await repo.delete(created.id)
    assert deleted is True

    repo.query = MagicMock(return_value=SimpleNamespace(count=AsyncMock(return_value=11)))
    assert await repo.count() == 11


@pytest.mark.asyncio
async def test_base_repository_get_all_uses_query_builder() -> None:
    session = MagicMock()
    repo = BaseRepository(User, session)

    qb = SimpleNamespace(
        offset=MagicMock(return_value=None),
    )
    qb.offset = MagicMock(return_value=qb)
    qb.limit = MagicMock(return_value=qb)
    qb.all = AsyncMock(return_value=["a"])

    repo.query = MagicMock(return_value=qb)
    rows = await repo.get_all(limit=3, offset=2)

    assert rows == ["a"]
    qb.offset.assert_called_once_with(2)
    qb.limit.assert_called_once_with(3)


@pytest.mark.asyncio
async def test_sync_service_update_complete_and_recent_jobs() -> None:
    job = SimpleNamespace(id=uuid4(), status="running", completed_at=None)
    session = MagicMock()
    session.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=job),
            FakeResult(one_value=job),
            FakeResult(all_value=[job]),
            FakeResult(all_value=[job]),
        ]
    )
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    service = SyncService(session)

    updated = await service.update_sync_job(job.id, {"status": "partial"})
    assert updated is job
    assert job.status == "partial"

    completed = await service.complete_sync_job(job.id)
    assert completed is True
    assert job.status == "completed"
    assert job.completed_at is not None

    jobs = await service.get_sync_jobs(limit=5)
    recent = await service.get_recent_sync_jobs(limit=3)
    assert jobs == [job]
    assert recent == [job]


@pytest.mark.asyncio
async def test_sync_service_complete_missing_job_returns_false() -> None:
    session = MagicMock()
    session.exec = AsyncMock(return_value=FakeResult(one_value=None))
    service = SyncService(session)

    assert await service.complete_sync_job(uuid4()) is False


@pytest.mark.asyncio
async def test_sync_service_sync_media_success_and_failure_paths() -> None:
    session = MagicMock()
    service = SyncService(session)

    created_job = SimpleNamespace(id=uuid4())
    service.create_sync_job = AsyncMock(return_value=created_job)
    service.update_sync_job = AsyncMock()

    count = await service.sync_media_from_anilist(limit=2)
    assert count == 0
    assert service.update_sync_job.await_count == 1

    async def explode(*args, **kwargs):
        raise RuntimeError("boom")

    service.update_sync_job = AsyncMock(side_effect=explode)
    service.create_sync_job = AsyncMock(return_value=created_job)

    with pytest.raises(RuntimeError):
        await service.sync_media_from_anilist(limit=1)


@pytest.mark.asyncio
async def test_sync_service_backfill_and_update_or_create_helpers(monkeypatch) -> None:
    media_id = uuid4()
    # backfill_missing_metadata now loads MediaExternalIds and runs adapter
    media = SimpleNamespace(
        id=media_id,
        metadata_synced_at=None,
        media_type="anime",
    )
    ext_ids = SimpleNamespace(
        anilist_id=12345,
        mangadex_id=None,
    )

    session1 = MagicMock()
    session1.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=media),     # backfill: select MediaEntry
            FakeResult(one_value=ext_ids),   # backfill: select MediaExternalIds
        ]
    )

    svc1 = SyncService(session1)
    # adapter returns processed_items=0 from autouse stub, so 0 > 0 is False
    assert await svc1.backfill_missing_metadata(media_id) is False

    # Second call: media not found
    session2 = MagicMock()
    session2.exec = AsyncMock(return_value=FakeResult(one_value=None))
    svc2 = SyncService(session2)
    assert await svc2.backfill_missing_metadata(uuid4()) is False

    # update_or_create_media_from_anilist — monkeypatch MediaEntry AFTER backfill
    # so the real MediaEntry is used for select() in backfill_missing_metadata
    class FakeMediaEntry:
        # Class attrs so hasattr(MediaEntry, k) returns True for common fields
        title_romaji = ""
        title_english = None
        title_native = None
        media_type = "anime"
        format = None
        status = "finished"
        is_adult = False
        metadata_synced_at = None
        updated_at = None
        deleted_at = None
        synopsis = None
        cover_image_large = None
        cover_image_medium = None
        banner_image = None
        episode_count = None
        chapter_count = None
        volume_count = None
        duration_minutes = None
        average_score = None
        popularity = None
        trending = None
        season = None
        season_year = None
        start_date = None
        end_date = None
        country_of_origin = None

        def __init__(self, **kwargs):
            self.id = uuid4()
            for key, value in kwargs.items():
                setattr(self, key, value)

    monkeypatch.setattr("src.app.services.sync_service.MediaEntry", FakeMediaEntry)

    session3 = MagicMock()
    session3.exec = AsyncMock(
        side_effect=[
            FakeResult(one_value=None),  # create: select MediaExternalIds by anilist_id
        ]
    )
    session3.add = MagicMock()
    session3.commit = AsyncMock()
    session3.refresh = AsyncMock()
    session3.flush = AsyncMock()

    svc3 = SyncService(session3)
    entry = await svc3.update_or_create_media_from_anilist(
        {
            "id": 99999,
            "title": {"romaji": "Test Anime", "english": "Test Anime"},
            "type": "ANIME",
            "format": "TV",
            "status": "FINISHED",
        }
    )
    assert entry.title_romaji == "Test Anime"


@pytest.mark.asyncio
async def test_sync_service_create_sync_job_commits_and_refreshes(monkeypatch) -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    class FakeSyncJob:
        def __init__(self, **kwargs):
            self.id = kwargs.get("id", uuid4())
            for key, value in kwargs.items():
                setattr(self, key, value)

    monkeypatch.setattr("src.app.services.sync_service.SyncJob", FakeSyncJob)

    service = SyncService(session)
    job = await service.create_sync_job("weekly_refresh", total_items=10)

    assert job.job_type == "weekly_refresh"
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()
