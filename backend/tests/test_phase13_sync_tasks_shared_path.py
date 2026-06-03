from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.app.workers import sync_tasks


@pytest.mark.parametrize(
    ("task_func", "expected_source", "kwargs", "expected"),
    [
        (sync_tasks.seed_database_task, "anime-offline", {"batch_size": 7, "dry_run": True}, {"batch_size": 7, "dry_run": True}),
        (
            sync_tasks.backfill_anilist_task,
            "anilist",
            {"limit": 12, "batch_size": 4, "only_unsynced": True},
            {"limit": 12, "batch_size": 4, "only_unsynced": True},
        ),
        (sync_tasks.mangadex_detail_task, "mangadex", {"limit": 9, "dry_run": True}, {"limit": 9, "dry_run": True}),
        (sync_tasks.weekly_refresh_task, "jikan", {"limit": 3}, {"limit": 3}),
    ],
)
def test_source_tasks_delegate_to_shared_seed_entrypoint(monkeypatch, task_func, expected_source, kwargs, expected):
    called: dict[str, object] = {}

    async def _fake_run_seed_source(**run_kwargs):
        called.update(run_kwargs)
        return {
            "source": expected_source,
            "job_id": "job-1",
            "status": "completed",
            "processed_items": 7,
            "failed_items": 0,
        }

    monkeypatch.setattr(sync_tasks, "run_seed_source", _fake_run_seed_source)

    result = task_func(**kwargs)

    assert called["source"] == expected_source
    for key, value in expected.items():
        assert called[key] == value
    assert result["status"] == "completed"


def test_seed_all_task_delegates_to_shared_orchestrator(monkeypatch):
    called: dict[str, object] = {}

    async def _fake_run_seed_all(**kwargs):
        called.update(kwargs)
        return {
            "source": "all",
            "job_id": "job-all",
            "status": "completed",
            "processed_items": 50,
            "failed_items": 0,
            "steps": [],
        }

    monkeypatch.setattr(sync_tasks, "run_seed_all", _fake_run_seed_all)

    result = sync_tasks.seed_all_task(dry_run=True, resume_job_id="resume-1", batch_size=25, limit=10)

    assert called == {
        "dry_run": True,
        "resume_job_id": "resume-1",
        "batch_size": 25,
        "limit": 10,
    }
    assert result["source"] == "all"


def test_source_task_returns_standardized_phase_payload(monkeypatch):
    async def _fake_run_seed_source(**kwargs):
        return {
            "source": "anilist",
            "job_id": "job-1",
            "status": "completed",
            "processed_items": 3,
            "failed_items": 0,
        }

    monkeypatch.setattr(sync_tasks, "run_seed_source", _fake_run_seed_source)

    result = sync_tasks.backfill_anilist_task()

    assert result["phase"] == "task"
    assert "duration_ms" in result
    assert result["duration_ms"] >= 0


def test_scheduled_compose_payload_shape_is_consistent(monkeypatch):
    class _FakeChain:
        def apply_async(self):
            return SimpleNamespace(id="workflow-1")

    monkeypatch.setattr(sync_tasks, "chain", lambda *args: _FakeChain())
    monkeypatch.setattr(sync_tasks, "backfill_anilist_task", SimpleNamespace(s=lambda **kwargs: SimpleNamespace()))
    monkeypatch.setattr(sync_tasks, "mangadex_detail_task", SimpleNamespace(s=lambda **kwargs: SimpleNamespace()))

    result = sync_tasks.daily_refresh_compose_task()

    assert result["phase"] == "task"
    assert result["source"] == "daily-refresh-compose"
    assert result["status"] == "queued"
    assert "duration_ms" in result


def test_source_task_retries_on_failure(monkeypatch):
    async def _boom(**kwargs):
        raise RuntimeError("upstream failed")

    monkeypatch.setattr(sync_tasks, "run_seed_source", _boom)

    retry_called: list[dict[str, object]] = []

    def _fake_retry_or_raise(self, exc):
        retry_called.append({"self": self, "exc": exc})

    monkeypatch.setattr(sync_tasks, "_retry_or_raise", _fake_retry_or_raise)

    sync_tasks.seed_database_task(batch_size=10)

    assert len(retry_called) == 1
    assert str(retry_called[0]["exc"]) == "upstream failed"


def test_sync_and_notification_task_routes_are_separated():
    sync_route = sync_tasks.celery_app.conf.task_routes["sync.*"]["queue"]
    notification_route = sync_tasks.celery_app.conf.task_routes["notifications.*"]["queue"]

    assert sync_route == "sync"
    assert notification_route == "notifications"


def test_scheduled_refresh_beat_entries_registered():
    beat_schedule = sync_tasks.celery_app.conf.beat_schedule

    assert beat_schedule["sync-daily-refresh-compose"]["task"] == "sync.daily_refresh_compose"
    assert beat_schedule["sync-weekly-refresh-compose"]["task"] == "sync.weekly_refresh_compose"


def test_daily_refresh_compose_wires_existing_shared_tasks(monkeypatch):
    calls: list[tuple[str, dict[str, object]]] = []

    class _FakeSig:
        def __init__(self, label: str, kwargs: dict[str, object]):
            self.label = label
            self.kwargs = kwargs

    class _FakeTask:
        def __init__(self, label: str):
            self.label = label

        def s(self, **kwargs):
            calls.append((self.label, kwargs))
            return _FakeSig(self.label, kwargs)

    class _FakeChain:
        def __init__(self, signatures):
            self.signatures = signatures

        def apply_async(self):
            return SimpleNamespace(id="chain-daily-1")

    def _fake_chain(*signatures):
        return _FakeChain(signatures)

    monkeypatch.setattr(sync_tasks, "backfill_anilist_task", _FakeTask("anilist"))
    monkeypatch.setattr(sync_tasks, "mangadex_detail_task", _FakeTask("mangadex"))
    monkeypatch.setattr(sync_tasks, "chain", _fake_chain)

    result = sync_tasks.daily_refresh_compose_task()

    assert result["status"] == "queued"
    assert result["workflow_id"] == "chain-daily-1"
    assert calls == [
        ("anilist", {"only_unsynced": True}),
        ("mangadex", {}),
    ]


def test_weekly_refresh_compose_wires_existing_shared_tasks(monkeypatch):
    calls: list[tuple[str, dict[str, object]]] = []

    class _FakeSig:
        def __init__(self, label: str, kwargs: dict[str, object]):
            self.label = label
            self.kwargs = kwargs

    class _FakeTask:
        def __init__(self, label: str):
            self.label = label

        def s(self, **kwargs):
            calls.append((self.label, kwargs))
            return _FakeSig(self.label, kwargs)

    class _FakeChain:
        def __init__(self, signatures):
            self.signatures = signatures

        def apply_async(self):
            return SimpleNamespace(id="chain-weekly-1")

    def _fake_chain(*signatures):
        return _FakeChain(signatures)

    monkeypatch.setattr(sync_tasks, "seed_database_task", _FakeTask("seed"))
    monkeypatch.setattr(sync_tasks, "backfill_anilist_task", _FakeTask("anilist"))
    monkeypatch.setattr(sync_tasks, "mangadex_detail_task", _FakeTask("mangadex"))
    monkeypatch.setattr(sync_tasks, "weekly_refresh_task", _FakeTask("jikan"))
    monkeypatch.setattr(sync_tasks, "chain", _fake_chain)

    result = sync_tasks.weekly_refresh_compose_task()

    assert result["status"] == "queued"
    assert result["workflow_id"] == "chain-weekly-1"
    assert calls == [
        ("seed", {}),
        ("anilist", {"only_unsynced": False}),
        ("mangadex", {}),
        ("jikan", {}),
    ]
