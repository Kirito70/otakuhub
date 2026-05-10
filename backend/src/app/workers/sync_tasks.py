"""Celery tasks for data synchronization."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from uuid import UUID

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
    """Import user's anime/manga list from external provider."""
    logger.info(f"Starting user list import task for user {user_id} from {provider}")

    try:
        result = {
            "task": "import_user_list",
            "status": "completed",
            "user_id": str(user_id),
            "provider": provider,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        logger.info(f"User list import completed for {user_id}")
        return result

    except Exception as e:
        logger.error(f"User list import failed: {e}")
        raise


@celery_app.task(bind=True, name="sync.process_new_episodes")
def process_new_episodes_task(self) -> dict[str, Any]:
    """Process new episodes/chapters for notification."""
    logger.info("Starting new episodes processing task")

    try:
        result = {
            "task": "process_new_episodes",
            "status": "completed",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        logger.info("New episodes processing completed")
        return result

    except Exception as e:
        logger.error(f"New episodes processing failed: {e}")
        raise
