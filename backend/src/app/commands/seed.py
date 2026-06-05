"""Data seeding commands."""

from __future__ import annotations

import asyncio
import logging
from time import perf_counter

import typer

from src.app.sync.entrypoints import run_seed_all, run_seed_source
from src.app.sync.observability import build_log_payload, duration_ms_since

app = typer.Typer(name="seed", help="Data seed commands")
logger = logging.getLogger(__name__)



def _execute_and_print(*, source: str, **kwargs: object) -> None:
    started_at = perf_counter()
    result = asyncio.run(run_seed_source(source=source, **kwargs))
    logger.info(
        "seed_command_completed",
        extra=build_log_payload(
            source=str(result["source"]),
            phase="command",
            job_id=str(result["job_id"]),
            status=str(result["status"]),
            processed_items=int(result["processed_items"]),
            failed_items=int(result["failed_items"]),
            duration_ms=duration_ms_since(started_at),
        ),
    )
    typer.echo(
        f"source={result['source']} job_id={result['job_id']} status={result['status']} "
        f"processed_items={result['processed_items']} failed_items={result['failed_items']}"
    )


@app.command("anime-offline")
def seed_anime_offline(batch_size: int = typer.Option(50, "--batch-size"), dry_run: bool = False) -> None:
    _execute_and_print(source="anime-offline", batch_size=batch_size, dry_run=dry_run)


@app.command("anilist")
def seed_anilist(
    limit: int = typer.Option(100, "--limit"),
    only_unsynced: bool = typer.Option(False, "--only-unsynced"),
) -> None:
    _execute_and_print(source="anilist", limit=limit, only_unsynced=only_unsynced)


@app.command("mangadex")
def seed_mangadex(limit: int = typer.Option(100, "--limit")) -> None:
    _execute_and_print(source="mangadex", limit=limit)


@app.command("jikan")
def seed_jikan(limit: int = typer.Option(100, "--limit")) -> None:
    _execute_and_print(source="jikan", limit=limit)


@app.command("anikoto-full")
def seed_anikoto_full(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int | None = typer.Option(None, "--max-pages"),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Sync the full Anikoto/MegaPlay provider catalog IDs into source tables."""
    _execute_and_print(
        source="anikoto_full_catalog",
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )


@app.command("megaplay-full")
def seed_megaplay_full(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int | None = typer.Option(None, "--max-pages"),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Sync all anime IDs needed for MegaPlay playback using the Anikoto catalog API."""
    _execute_and_print(
        source="anikoto_full_catalog",
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )


@app.command("anikoto-recent")
def seed_anikoto_recent(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int = typer.Option(5, "--max-pages", min=1),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Sync recent Anikoto/MegaPlay provider IDs; same path used by daily Celery refresh."""
    _execute_and_print(
        source="anikoto_recent_refresh",
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )


@app.command("megaplay-recent")
def seed_megaplay_recent(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int = typer.Option(5, "--max-pages", min=1),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Sync recent anime IDs needed for MegaPlay playback; same path used by daily Celery refresh."""
    _execute_and_print(
        source="anikoto_recent_refresh",
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )


@app.command("run", hidden=True)
def seed_run_compat() -> None:
    """Deprecated compatibility alias for legacy seed entrypoint."""
    typer.echo(
        "DEPRECATED: `otakuhub seed run` is deprecated. "
        "Use `otakuhub seed anime-offline` (or `otakuhub seed all`) instead."
    )
    _execute_and_print(source="anime-offline", batch_size=50, dry_run=False)


@app.command("all")
def seed_all(
    dry_run: bool = typer.Option(False, "--dry-run"),
    resume_job_id: str | None = typer.Option(None, "--resume-job-id"),
    batch_size: int = typer.Option(50, "--batch-size"),
    limit: int = typer.Option(100, "--limit"),
    user_id: str | None = typer.Option(None, "--user-id", help="UUID of user to associate with this seed job"),
) -> None:
    started_at = perf_counter()
    result = asyncio.run(
        run_seed_all(
            dry_run=dry_run,
            resume_job_id=resume_job_id,
            batch_size=batch_size,
            limit=limit,
            user_id=user_id,
        )
    )
    logger.info(
        "seed_all_command_completed",
        extra=build_log_payload(
            source=str(result["source"]),
            phase="command",
            job_id=str(result["job_id"]),
            status=str(result["status"]),
            processed_items=int(result["processed_items"]),
            failed_items=int(result["failed_items"]),
            duration_ms=duration_ms_since(started_at),
            steps=result.get("steps", []),
            resumed_from=result.get("resumed_from"),
        ),
    )
    typer.echo(
        f"source={result['source']} job_id={result['job_id']} status={result['status']} "
        f"processed_items={result['processed_items']} failed_items={result['failed_items']} "
        f"steps={len(result.get('steps', []))} dry_run={result.get('dry_run')}"
    )
