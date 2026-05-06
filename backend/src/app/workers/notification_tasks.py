"""Celery tasks for notification fan-out and delivery."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from celery.utils.log import get_task_logger

from src.app.config import settings
from src.app.external import AppriseClient
from src.app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(bind=True, name="notifications.new_episode")
def send_new_episode_notifications_task(
    self,
    episodes: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Phase 11.2 — Send new episode notifications via Apprise."""
    logger.info("Starting new episode notification task")

    events = episodes or []
    apprise_client = AppriseClient(settings.apprise_urls)

    if not apprise_client.is_configured:
        logger.warning("Apprise is not configured; skipping external delivery")

    delivered = 0
    failed = 0

    for event in events:
        title = str(event.get("title") or "New Episode Available")
        body = str(event.get("body") or "A tracked show has a new episode.")

        try:
            sent = apprise_client.send_notification(title=title, body=body)
            if sent:
                delivered += 1
            else:
                failed += 1
        except Exception as exc:  # defensive for provider/runtime failures
            logger.error("Failed to deliver episode notification: %s", exc)
            failed += 1

    result = {
        "task": "notifications.new_episode",
        "status": "completed",
        "configured_targets": apprise_client.configured_targets,
        "processed_items": len(events),
        "delivered_items": delivered,
        "failed_items": failed,
        "timestamp": datetime.utcnow().isoformat(),
    }
    logger.info(
        "New episode notifications task completed: %s processed, %s delivered, %s failed",
        len(events),
        delivered,
        failed,
    )
    return result


@celery_app.task(bind=True, name="notifications.new_chapter")
def send_new_chapter_notifications_task(
    self,
    chapters: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Phase 11.3 — Send new chapter notifications via Apprise."""
    logger.info("Starting new chapter notification task")

    events = chapters or []
    apprise_client = AppriseClient(settings.apprise_urls)

    if not apprise_client.is_configured:
        logger.warning("Apprise is not configured; skipping external delivery")

    delivered = 0
    failed = 0

    for event in events:
        title = str(event.get("title") or "New Chapter Available")
        body = str(event.get("body") or "A tracked series has a new chapter.")

        try:
            sent = apprise_client.send_notification(title=title, body=body)
            if sent:
                delivered += 1
            else:
                failed += 1
        except Exception as exc:
            logger.error("Failed to deliver chapter notification: %s", exc)
            failed += 1

    result = {
        "task": "notifications.new_chapter",
        "status": "completed",
        "configured_targets": apprise_client.configured_targets,
        "processed_items": len(events),
        "delivered_items": delivered,
        "failed_items": failed,
        "timestamp": datetime.utcnow().isoformat(),
    }
    logger.info(
        "New chapter notifications task completed: %s processed, %s delivered, %s failed",
        len(events),
        delivered,
        failed,
    )
    return result


@celery_app.task(bind=True, name="notifications.watch_party_reminder")
def send_watch_party_reminder_notifications_task(
    self,
    parties: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    """Phase 11.4 — Send watch party reminder notifications via Apprise."""
    logger.info("Starting watch party reminder notification task")

    events = parties or []
    apprise_client = AppriseClient(settings.apprise_urls)

    if not apprise_client.is_configured:
        logger.warning("Apprise is not configured; skipping external delivery")

    delivered = 0
    failed = 0

    for event in events:
        title = str(event.get("title") or "Watch Party Reminder")
        body = str(
            event.get("body")
            or "A watch party you joined is starting soon."
        )

        try:
            sent = apprise_client.send_notification(title=title, body=body)
            if sent:
                delivered += 1
            else:
                failed += 1
        except Exception as exc:
            logger.error("Failed to deliver watch party reminder: %s", exc)
            failed += 1

    result = {
        "task": "notifications.watch_party_reminder",
        "status": "completed",
        "configured_targets": apprise_client.configured_targets,
        "processed_items": len(events),
        "delivered_items": delivered,
        "failed_items": failed,
        "timestamp": datetime.utcnow().isoformat(),
    }
    logger.info(
        "Watch party reminder notifications task completed: %s processed, %s delivered, %s failed",
        len(events),
        delivered,
        failed,
    )
    return result
