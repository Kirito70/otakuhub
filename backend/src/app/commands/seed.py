"""Data seeding commands."""

from __future__ import annotations

import asyncio
import logging
from time import perf_counter

import typer
from sqlalchemy import func
from sqlmodel import select

from src.app.database import AsyncSessionLocal
from src.app.models.media_source_episode import MediaSourceEpisode
from src.app.models.media_source_mapping import MediaSourceMapping
from src.app.sync.entrypoints import run_seed_all, run_seed_source
from src.app.sync.observability import build_log_payload, duration_ms_since

app = typer.Typer(name="seed", help="Data seed commands")
logger = logging.getLogger(__name__)


async def _provider_counts() -> dict[str, int]:
    async with AsyncSessionLocal() as session:
        total_mappings = (await session.exec(select(func.count()).select_from(MediaSourceMapping))).one()
        total_episodes = (await session.exec(select(func.count()).select_from(MediaSourceEpisode))).one()
        matched = (await session.exec(select(func.count()).select_from(MediaSourceMapping).where(MediaSourceMapping.mapping_status == "matched"))).one()
        unmatched = (await session.exec(select(func.count()).select_from(MediaSourceMapping).where(MediaSourceMapping.mapping_status == "unmatched"))).one()
        linked = (await session.exec(select(func.count()).select_from(MediaSourceMapping).where(MediaSourceMapping.media_id.is_not(None)))).one()
        return {
            "mappings": int(total_mappings),
            "episodes": int(total_episodes),
            "matched": int(matched),
            "unmatched": int(unmatched),
            "linked_to_media_entries": int(linked),
        }


async def _execute_source(*, source: str, **kwargs: object) -> tuple[dict[str, object], dict[str, int] | None, dict[str, int] | None]:
    is_provider_source = source in {"anikoto_full_catalog", "anikoto_recent_refresh"}
    before = await _provider_counts() if is_provider_source and not kwargs.get("dry_run") else None
    result = await run_seed_source(source=source, **kwargs)
    after = await _provider_counts() if is_provider_source and not kwargs.get("dry_run") else None
    return result, before, after


def _execute_and_print(*, source: str, **kwargs: object) -> None:
    started_at = perf_counter()
    result, before_counts, after_counts = asyncio.run(_execute_source(source=source, **kwargs))
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
    if source in {"anikoto_full_catalog", "anikoto_recent_refresh"}:
        if kwargs.get("dry_run"):
            typer.echo("provider_tables=dry_run_no_rows_written")
            typer.echo("note=MegaPlay/Anikoto rows are stored in media_source_mappings and media_source_episodes, not media_entries")
        elif before_counts is not None and after_counts is not None:
            typer.echo(
                "provider_tables="
                f"media_source_mappings {before_counts['mappings']}->{after_counts['mappings']} "
                f"(+{after_counts['mappings'] - before_counts['mappings']}), "
                f"media_source_episodes {before_counts['episodes']}->{after_counts['episodes']} "
                f"(+{after_counts['episodes'] - before_counts['episodes']})"
            )
            typer.echo(
                "provider_match_status="
                f"matched={after_counts['matched']} unmatched={after_counts['unmatched']} "
                f"linked_to_media_entries={after_counts['linked_to_media_entries']}"
            )
            typer.echo("note=MegaPlay/Anikoto catalog IDs are provider rows; media_entries is canonical AniList/anime-offline metadata")


@app.command("anime-offline")
def seed_anime_offline(batch_size: int = typer.Option(50, "--batch-size"), dry_run: bool = False) -> None:
    _execute_and_print(source="anime-offline", batch_size=batch_size, dry_run=dry_run)


@app.command("anilist")
def seed_anilist(
    limit: int = typer.Option(0, "--limit", help="Max entries to backfill (0 = no limit)"),
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
