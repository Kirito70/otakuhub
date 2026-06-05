"""Celery process and task commands."""

from __future__ import annotations

import subprocess

import typer

from src.app.workers.sync_tasks import (
    anikoto_full_catalog_task,
    anikoto_recent_refresh_task,
    seed_database_task,
    weekly_refresh_task,
)
from src.app.workers.notification_tasks import (
    send_new_chapter_notifications_task,
    send_new_episode_notifications_task,
    send_watch_party_reminder_notifications_task,
)

app = typer.Typer(name="celery", help="Celery worker/beat/task commands")


@app.command("worker")
def run_worker(loglevel: str = "info", queue: str = "sync") -> None:
    """Run Celery worker for OtakuHub sync tasks."""
    cmd = [
        "celery",
        "-A",
        "src.app.workers.celery_app:celery_app",
        "worker",
        "-l",
        loglevel,
        "-Q",
        queue,
    ]
    raise typer.Exit(subprocess.call(cmd))


@app.command("beat")
def run_beat(loglevel: str = "info") -> None:
    """Run Celery beat scheduler for periodic jobs."""
    cmd = [
        "celery",
        "-A",
        "src.app.workers.celery_app:celery_app",
        "beat",
        "-l",
        loglevel,
    ]
    raise typer.Exit(subprocess.call(cmd))


@app.command("seed")
def enqueue_seed(batch_size: int = 50) -> None:
    """Enqueue database seed task on Celery."""
    result = seed_database_task.delay(batch_size=batch_size)
    typer.echo(f"✓ Seed task enqueued: {result.id}")


@app.command("weekly-refresh")
def enqueue_weekly_refresh() -> None:
    """Enqueue weekly refresh sync task on Celery."""
    result = weekly_refresh_task.delay()
    typer.echo(f"✓ Weekly refresh task enqueued: {result.id}")


@app.command("anikoto-full")
def enqueue_anikoto_full(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int | None = typer.Option(None, "--max-pages"),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Enqueue full Anikoto/MegaPlay provider catalog sync on Celery."""
    result = anikoto_full_catalog_task.delay(
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )
    typer.echo(f"✓ Anikoto full catalog sync enqueued: {result.id}")


@app.command("megaplay-full")
def enqueue_megaplay_full(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int | None = typer.Option(None, "--max-pages"),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Enqueue full MegaPlay provider catalog sync via Anikoto discovery."""
    result = anikoto_full_catalog_task.delay(
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )
    typer.echo(f"✓ MegaPlay full catalog sync enqueued: {result.id}")


@app.command("anikoto-recent")
def enqueue_anikoto_recent(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int = typer.Option(5, "--max-pages", min=1),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Enqueue bounded recent Anikoto/MegaPlay provider refresh on Celery."""
    result = anikoto_recent_refresh_task.delay(
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )
    typer.echo(f"✓ Anikoto recent refresh enqueued: {result.id}")


@app.command("megaplay-recent")
def enqueue_megaplay_recent(
    per_page: int = typer.Option(20, "--per-page", min=1, max=50),
    max_pages: int = typer.Option(5, "--max-pages", min=1),
    refresh_details: bool = typer.Option(True, "--refresh-details/--no-refresh-details"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Enqueue bounded recent MegaPlay provider refresh via Anikoto discovery."""
    result = anikoto_recent_refresh_task.delay(
        per_page=per_page,
        max_pages=max_pages,
        refresh_details=refresh_details,
        dry_run=dry_run,
    )
    typer.echo(f"✓ MegaPlay recent refresh enqueued: {result.id}")


@app.command("new-episode-notifications")
def enqueue_new_episode_notifications() -> None:
    """Enqueue phase 11.2 new-episode notification worker task."""
    result = send_new_episode_notifications_task.delay()
    typer.echo(f"✓ New episode notification task enqueued: {result.id}")


@app.command("new-chapter-notifications")
def enqueue_new_chapter_notifications() -> None:
    """Enqueue phase 11.3 new-chapter notification worker task."""
    result = send_new_chapter_notifications_task.delay()
    typer.echo(f"✓ New chapter notification task enqueued: {result.id}")


@app.command("watch-party-reminders")
def enqueue_watch_party_reminders() -> None:
    """Enqueue phase 11.4 watch-party reminder worker task."""
    result = send_watch_party_reminder_notifications_task.delay()
    typer.echo(f"✓ Watch party reminder task enqueued: {result.id}")
