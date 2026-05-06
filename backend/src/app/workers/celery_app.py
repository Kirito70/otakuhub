"""Celery application for OtakuHub."""

from celery import Celery
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
)

# Configure task routing (optional)
celery_app.conf.task_routes = {
    "src.app.workers.sync_tasks.*": {"queue": "sync"},
    "src.app.workers.notification_tasks.*": {"queue": "sync"},
}

__all__ = ["celery_app"]
