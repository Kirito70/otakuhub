"""Celery application for OtakuHub."""

from celery import Celery

try:
    from celery.schedules import crontab
except Exception:  # pragma: no cover - fallback for local test Celery stub
    def crontab(**kwargs):  # type: ignore[no-redef]
        return kwargs

from src.app.config import settings

# Create Celery app
celery_app = Celery(
    "otakuhub",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "src.app.workers.sync_tasks",
        "src.app.workers.notification_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    # Rate limit configuration for external APIs
    redis_max_connections=20,
    redis_retry_on_timeout=True,
    beat_schedule={
        # Daily at 02:00 UTC: keep frequently-changing metadata fresh.
        "sync-daily-refresh-compose": {
            "task": "sync.daily_refresh_compose",
            "schedule": crontab(hour=2, minute=0),
        },
        # Weekly Sunday at 01:00 UTC: run full refresh composition.
        "sync-weekly-refresh-compose": {
            "task": "sync.weekly_refresh_compose",
            "schedule": crontab(hour=1, minute=0, day_of_week=0),
        },
    },
)

# Configure task routing
celery_app.conf.task_routes = {
    "sync.*": {"queue": "sync"},
    "notifications.*": {"queue": "notifications"},
}

__all__ = ["celery_app"]
