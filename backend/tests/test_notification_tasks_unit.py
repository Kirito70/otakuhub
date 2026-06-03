from __future__ import annotations

from typing import Any

import pytest

from src.app.workers.notification_tasks import (
    send_new_chapter_notifications_task,
    send_new_episode_notifications_task,
    send_watch_party_reminder_notifications_task,
)


class FakeAppriseClient:
    def __init__(self, _urls: str, *, configured: bool = True, outcomes: list[bool] | None = None, raises_at: set[int] | None = None):
        self.is_configured = configured
        self.configured_targets = 1 if configured else 0
        self._outcomes = outcomes or []
        self._raises_at = raises_at or set()
        self._calls = 0

    def send_notification(self, *, title: str, body: str) -> bool:
        idx = self._calls
        self._calls += 1
        if idx in self._raises_at:
            raise RuntimeError("delivery failed")
        if idx < len(self._outcomes):
            return self._outcomes[idx]
        return True


@pytest.mark.parametrize(
    "fn,task_name,default_title,default_body",
    [
        (send_new_episode_notifications_task, "notifications.new_episode", "New Episode Available", "A tracked show has a new episode."),
        (send_new_chapter_notifications_task, "notifications.new_chapter", "New Chapter Available", "A tracked series has a new chapter."),
        (send_watch_party_reminder_notifications_task, "notifications.watch_party_reminder", "Watch Party Reminder", "A watch party you joined is starting soon."),
    ],
)
def test_notification_task_defaults_and_success(monkeypatch, fn: Any, task_name: str, default_title: str, default_body: str) -> None:
    monkeypatch.setattr(
        "src.app.workers.notification_tasks.AppriseClient",
        lambda urls: FakeAppriseClient(urls, configured=True, outcomes=[True]),
    )

    result = fn([{}])

    assert result["task"] == task_name
    assert result["status"] == "completed"
    assert result["processed_items"] == 1
    assert result["delivered_items"] == 1
    assert result["failed_items"] == 0
    assert "timestamp" in result


def test_new_episode_task_counts_failed_and_exceptions(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.app.workers.notification_tasks.AppriseClient",
        lambda urls: FakeAppriseClient(urls, configured=True, outcomes=[True, False], raises_at={2}),
    )

    events = [
        {"title": "t1", "body": "b1"},
        {"title": "t2", "body": "b2"},
        {"title": "t3", "body": "b3"},
    ]
    result = send_new_episode_notifications_task(events)

    assert result["processed_items"] == 3
    assert result["delivered_items"] == 1
    assert result["failed_items"] == 2


def test_new_chapter_task_handles_unconfigured_apprise(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.app.workers.notification_tasks.AppriseClient",
        lambda urls: FakeAppriseClient(urls, configured=False, outcomes=[False]),
    )

    result = send_new_chapter_notifications_task([{"title": "chapter"}])

    assert result["configured_targets"] == 0
    assert result["processed_items"] == 1
    assert result["delivered_items"] == 0
    assert result["failed_items"] == 1


def test_watch_party_task_with_none_events(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.app.workers.notification_tasks.AppriseClient",
        lambda urls: FakeAppriseClient(urls, configured=True),
    )

    result = send_watch_party_reminder_notifications_task(None)

    assert result["processed_items"] == 0
    assert result["delivered_items"] == 0
    assert result["failed_items"] == 0
