"""Celery tasks for data synchronization."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from time import perf_counter
from typing import Any
from uuid import UUID, uuid4

try:
    from celery.canvas import chain
except Exception:  # pragma: no cover - fallback for local test Celery stub
    def chain(*signatures):  # type: ignore[no-redef]
        class _InlineChain:
            def __init__(self, entries):
                self.entries = entries

            def apply_async(self):
                for entry in self.entries:
                    delay = getattr(entry, "delay", None)
                    if callable(delay):
                        delay()
                class _Result:
                    id = "inline-chain"
                return _Result()

        return _InlineChain(signatures)

from celery.utils.log import get_task_logger
from sqlmodel import select

from src.app.sync.entrypoints import run_seed_all, run_seed_source
from src.app.sync.observability import build_log_payload, duration_ms_since
from src.app.workers.celery_app import celery_app

logger = get_task_logger(__name__)

DEFAULT_RETRY_COUNTDOWN_SECONDS = 30


def _with_task_metadata(result: dict[str, Any], *, task_name: str, started_at: float) -> dict[str, Any]:
    payload = dict(result)
    payload.update(
        build_log_payload(
            source=str(payload.get("source", task_name)),
            phase="task",
            job_id=str(payload.get("job_id")) if payload.get("job_id") else None,
            status=str(payload.get("status", "completed")),
            processed_items=int(payload.get("processed_items", 0)),
            failed_items=int(payload.get("failed_items", 0)),
            duration_ms=duration_ms_since(started_at),
        )
    )
    payload["task"] = task_name
    payload["timestamp"] = datetime.now(UTC).isoformat()
    return payload


def _retry_or_raise(self: Any, exc: Exception) -> None:
    if self is None:
        raise exc
    raise self.retry(exc=exc, countdown=DEFAULT_RETRY_COUNTDOWN_SECONDS)


@celery_app.task(bind=True, name="sync.seed_database", max_retries=3)
def seed_database_task(
    self,
    *,
    batch_size: int = 50,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run anime-offline ingestion via shared orchestrator entrypoint."""
    logger.info("Starting anime-offline seed task")
    started_at = perf_counter()
    try:
        result = asyncio.run(
            run_seed_source(source="anime-offline", batch_size=batch_size, dry_run=dry_run)
        )
        return _with_task_metadata(result, task_name="sync.seed_database", started_at=started_at)
    except Exception as exc:
        logger.error("Anime-offline seed task failed: %s", exc)
        _retry_or_raise(self, exc)


@celery_app.task(bind=True, name="sync.backfill_anilist", max_retries=3)
def backfill_anilist_task(
    self,
    *,
    limit: int = 100,
    batch_size: int = 50,
    dry_run: bool = False,
    only_unsynced: bool = True,
) -> dict[str, Any]:
    """Run AniList backfill via shared orchestrator entrypoint."""
    logger.info("Starting AniList backfill task")
    started_at = perf_counter()
    try:
        result = asyncio.run(
            run_seed_source(
                source="anilist",
                limit=limit,
                batch_size=batch_size,
                dry_run=dry_run,
                only_unsynced=only_unsynced,
            )
        )
        return _with_task_metadata(result, task_name="sync.backfill_anilist", started_at=started_at)
    except Exception as exc:
        logger.error("AniList backfill task failed: %s", exc)
        _retry_or_raise(self, exc)


@celery_app.task(bind=True, name="sync.mangadex_detail", max_retries=3)
def mangadex_detail_task(
    self,
    *,
    limit: int = 100,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run MangaDex detail ingestion via shared orchestrator entrypoint."""
    logger.info("Starting MangaDex detail task")
    started_at = perf_counter()
    try:
        result = asyncio.run(
            run_seed_source(source="mangadex", limit=limit, dry_run=dry_run)
        )
        return _with_task_metadata(result, task_name="sync.mangadex_detail", started_at=started_at)
    except Exception as exc:
        logger.error("MangaDex detail task failed: %s", exc)
        _retry_or_raise(self, exc)


@celery_app.task(bind=True, name="sync.weekly_refresh", max_retries=3)
def weekly_refresh_task(
    self,
    *,
    limit: int = 100,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run Jikan weekly refresh via shared orchestrator entrypoint."""
    logger.info("Starting Jikan weekly refresh task")
    started_at = perf_counter()
    try:
        result = asyncio.run(run_seed_source(source="jikan", limit=limit, dry_run=dry_run))
        return _with_task_metadata(result, task_name="sync.weekly_refresh", started_at=started_at)
    except Exception as exc:
        logger.error("Weekly refresh task failed: %s", exc)
        _retry_or_raise(self, exc)


@celery_app.task(name="sync.daily_refresh_compose")
def daily_refresh_compose_task() -> dict[str, Any]:
    """Compose daily refresh flow from existing shared sync tasks only."""
    logger.info("Starting daily refresh composition")
    started_at = perf_counter()
    workflow = chain(
        backfill_anilist_task.s(only_unsynced=True),
        mangadex_detail_task.s(),
    )
    async_result = workflow.apply_async()
    return {
        **build_log_payload(
            source="daily-refresh-compose",
            phase="task",
            status="queued",
            duration_ms=duration_ms_since(started_at),
        ),
        "task": "sync.daily_refresh_compose",
        "workflow_id": async_result.id,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@celery_app.task(name="sync.weekly_refresh_compose")
def weekly_refresh_compose_task() -> dict[str, Any]:
    """Compose weekly refresh flow from existing shared sync tasks only."""
    logger.info("Starting weekly refresh composition")
    started_at = perf_counter()
    workflow = chain(
        seed_database_task.s(),
        backfill_anilist_task.s(only_unsynced=False),
        mangadex_detail_task.s(),
        weekly_refresh_task.s(),
    )
    async_result = workflow.apply_async()
    return {
        **build_log_payload(
            source="weekly-refresh-compose",
            phase="task",
            status="queued",
            duration_ms=duration_ms_since(started_at),
        ),
        "task": "sync.weekly_refresh_compose",
        "workflow_id": async_result.id,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@celery_app.task(bind=True, name="sync.seed_all", max_retries=3)
def seed_all_task(
    self,
    *,
    dry_run: bool = False,
    resume_job_id: str | None = None,
    batch_size: int = 50,
    limit: int = 100,
) -> dict[str, Any]:
    """Run umbrella all-source seed pipeline via shared orchestrator entrypoint."""
    logger.info("Starting seed-all task")
    started_at = perf_counter()
    try:
        result = asyncio.run(
            run_seed_all(
                dry_run=dry_run,
                resume_job_id=resume_job_id,
                batch_size=batch_size,
                limit=limit,
            )
        )
        return _with_task_metadata(result, task_name="sync.seed_all", started_at=started_at)
    except Exception as exc:
        logger.error("Seed-all task failed: %s", exc)
        _retry_or_raise(self, exc)


@celery_app.task(bind=True, name="sync.import_user_list")
def import_user_list_task(self, user_id: UUID, provider: str, username: str) -> dict[str, Any]:
    """Import user's anime/manga list from external provider.

    Creates a sync_jobs row and (in future) fetches the user's external list
    using stored OAuth tokens. For now, this is a skeleton that properly
    tracks the job lifecycle.
    """
    logger.info(f"Starting user list import for user {user_id} from {provider}")
    started_at = perf_counter()

    async def _run() -> dict[str, Any]:
        from src.app.database import AsyncSessionLocal
        from src.app.models.sync_job import SyncJob

        async with AsyncSessionLocal() as session:
            # Create sync job entry
            job = SyncJob(
                id=uuid4(),
                job_type=f"user_import_{provider}",
                user_id=user_id,
                status="running",
                started_at=datetime.now(UTC),
            )
            session.add(job)
            await session.commit()

            # TODO: Implement real AniList/MAL list import
            # Requires the user to have OAuth tokens stored in external_auth table
            # Then fetch from AniList GraphQL using stored access_token
            # For each entry in the list, upsert into user_list_entries
            # For now, mark as completed skeleton
            job.status = "completed"
            job.processed_items = 0
            job.completed_at = datetime.now(UTC)
            await session.commit()

            return {
                "task": "import_user_list",
                "status": "completed",
                "user_id": str(user_id),
                "provider": provider,
                "processed_items": 0,
                "job_id": str(job.id),
                "timestamp": datetime.now(UTC).isoformat(),
            }

    try:
        result = asyncio.run(_run())
        return _with_task_metadata(result, task_name="sync.import_user_list", started_at=started_at)
    except Exception as e:
        logger.error(f"User list import failed: {e}")
        raise


@celery_app.task(bind=True, name="sync.process_new_episodes")
def process_new_episodes_task(self) -> dict[str, Any]:
    """Process new episodes/chapters for notification.

    Queries the episodes and chapters tables for recently aired/published
    entries (within the last 24 hours), groups by media_id, and identifies
    users who are watching/reading those titles to create notification entries.
    """
    logger.info("Starting new episodes/chapters processing task")
    started_at = perf_counter()

    async def _run() -> dict[str, Any]:
        from src.app.database import AsyncSessionLocal
        from src.app.models.episode import Episode
        from src.app.models.chapter import Chapter
        from src.app.models.user_list_entry import UserListEntry
        from src.app.models.notification import Notification
        from src.app.models.enums import NotificationType

        async with AsyncSessionLocal() as session:
            now = datetime.now(UTC)
            cutoff = now - timedelta(hours=24)

            # Find recently aired episodes
            stmt_eps = (
                select(Episode)
                .where(Episode.air_date >= cutoff)
                .where(Episode.air_date <= now)
                .order_by(Episode.air_date.asc())
            )
            result = await session.execute(stmt_eps)
            new_episodes = result.scalars().all()

            # Find recently published chapters
            stmt_ch = (
                select(Chapter)
                .where(Chapter.published_at >= cutoff)
                .where(Chapter.published_at <= now)
                .order_by(Chapter.published_at.asc())
            )
            result = await session.execute(stmt_ch)
            new_chapters = result.scalars().all()

            # Group episodes by media_id for notification creation
            episode_media_ids = {ep.media_id for ep in new_episodes}
            chapter_media_ids = {ch.media_id for ch in new_chapters}

            # Determine which users are watching/reading these media
            watching_users: set[UUID] = set()
            reading_users: set[UUID] = set()

            if episode_media_ids:
                stmt_watch = (
                    select(UserListEntry)
                    .where(UserListEntry.media_id.in_(episode_media_ids))
                    .where(UserListEntry.status.in_(["watching", "rewatching"]))
                    .where(UserListEntry.deleted_at.is_(None))
                )
                result = await session.execute(stmt_watch)
                for entry in result.scalars().all():
                    watching_users.add(entry.user_id)

            if chapter_media_ids:
                stmt_read = (
                    select(UserListEntry)
                    .where(UserListEntry.media_id.in_(chapter_media_ids))
                    .where(UserListEntry.status.in_(["reading", "rereading"]))
                    .where(UserListEntry.deleted_at.is_(None))
                )
                result = await session.execute(stmt_read)
                for entry in result.scalars().all():
                    reading_users.add(entry.user_id)

            # Create notification entries for affected users
            notifications_created = 0
            for user_id in watching_users:
                for ep in new_episodes:
                    notif = Notification(
                        user_id=user_id,
                        type=NotificationType.new_episode,
                        title=f"New episode: {ep.episode_number}",
                        body=ep.title or f"Episode {ep.episode_number} has aired",
                        related_media_id=ep.media_id,
                    )
                    session.add(notif)
                    notifications_created += 1

            for user_id in reading_users:
                for ch in new_chapters:
                    notif = Notification(
                        user_id=user_id,
                        type=NotificationType.new_chapter,
                        title=f"New chapter: {ch.chapter_number}",
                        body=ch.title or f"Chapter {ch.chapter_number} has been published",
                        related_media_id=ch.media_id,
                    )
                    session.add(notif)
                    notifications_created += 1

            await session.commit()

            logger.info(
                f"New episodes/chapters processing completed: "
                f"{len(new_episodes)} episodes, {len(new_chapters)} chapters, "
                f"{notifications_created} notifications created"
            )

            return {
                "task": "process_new_episodes",
                "status": "completed",
                "new_episodes": len(new_episodes),
                "new_chapters": len(new_chapters),
                "notifications_created": notifications_created,
                "timestamp": now.isoformat(),
            }

    try:
        result = asyncio.run(_run())
        return _with_task_metadata(result, task_name="sync.process_new_episodes", started_at=started_at)
    except Exception as e:
        logger.error(f"New episodes processing failed: {e}")
        raise
