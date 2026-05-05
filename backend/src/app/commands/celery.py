"""Celery process and task commands."""

from __future__ import annotations

import subprocess

import typer

from src.app.workers.sync_tasks import seed_database_task, weekly_refresh_task

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
