"""Celery process and task commands."""

from __future__ import annotations

import subprocess

import typer

from src.app.workers.sync_tasks import seed_database_task, weekly_refresh_task
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
