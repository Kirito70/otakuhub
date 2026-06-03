from __future__ import annotations

import pytest

from src.app.sync.orchestrator import SeedOrchestrator


class FakeAdapter:
    def __init__(self, source: str, *, status: str = "completed", processed: int = 1, failed: int = 0):
        self.source = source
        self.status = status
        self.processed = processed
        self.failed = failed

    async def run(self, context):
        return type(
            "Result",
            (),
            {
                "source": context.source,
                "status": self.status,
                "processed_items": self.processed,
                "failed_items": self.failed,
                "errors": [] if self.status == "completed" else [{"item": "x", "source": self.source, "error": "boom"}],
            },
        )()


class FakeJobRunner:
    def __init__(self):
        self.started: list[str] = []
        self.completed_for_resume: list[str] = []
        self.finished: list[tuple[str, str]] = []

    async def start_job(self, *, source: str, total_items=None, user_id: str | None = None):
        self.started.append(source)
        return f"job-{source}-{len(self.started)}"

    async def progress(self, *, job_id: str, processed_items: int, failed_items: int):
        return None

    async def finish_completed(self, *, job_id: str, source: str = "unknown", resume_sources=None):
        self.finished.append((job_id, "completed"))

    async def finish_partial(self, *, job_id: str, errors, source: str = "unknown"):
        self.finished.append((job_id, "partial"))

    async def finish_failed(self, *, job_id: str, errors, source: str = "unknown"):
        self.finished.append((job_id, "failed"))

    async def get_completed_sources_for_resume(self, *, job_id: str):
        return self.completed_for_resume


@pytest.mark.asyncio
async def test_seed_all_runs_sources_in_order_and_finishes_completed():
    job_runner = FakeJobRunner()
    orchestrator = SeedOrchestrator(
        job_runner=job_runner,
        adapters={
            "anime-offline": FakeAdapter("anime-offline"),
            "anilist": FakeAdapter("anilist"),
            "mangadex": FakeAdapter("mangadex"),
            "jikan": FakeAdapter("jikan"),
        },
    )

    result = await orchestrator.run_all(dry_run=True)

    assert result["status"] == "completed"
    assert [step["source"] for step in result["steps"]] == ["anime-offline", "anilist", "mangadex", "jikan"]
    assert job_runner.started == ["all", "anime-offline", "anilist", "mangadex", "jikan"]


@pytest.mark.asyncio
async def test_seed_all_resume_skips_completed_sources():
    job_runner = FakeJobRunner()
    job_runner.completed_for_resume = ["anime-offline", "anilist"]
    orchestrator = SeedOrchestrator(
        job_runner=job_runner,
        adapters={
            "anime-offline": FakeAdapter("anime-offline"),
            "anilist": FakeAdapter("anilist"),
            "mangadex": FakeAdapter("mangadex"),
            "jikan": FakeAdapter("jikan"),
        },
    )

    result = await orchestrator.run_all(resume_job_id="umbrella-1")

    assert result["status"] == "completed"
    skipped = [step for step in result["steps"] if step["status"] == "skipped"]
    assert [step["source"] for step in skipped] == ["anime-offline", "anilist"]
    assert job_runner.started == ["all", "mangadex", "jikan"]


@pytest.mark.asyncio
async def test_seed_all_stops_on_failed_step_and_marks_umbrella_failed():
    job_runner = FakeJobRunner()
    orchestrator = SeedOrchestrator(
        job_runner=job_runner,
        adapters={
            "anime-offline": FakeAdapter("anime-offline"),
            "anilist": FakeAdapter("anilist", status="failed", failed=2),
            "mangadex": FakeAdapter("mangadex"),
            "jikan": FakeAdapter("jikan"),
        },
    )

    result = await orchestrator.run_all()

    assert result["status"] == "failed"
    assert [step["source"] for step in result["steps"]] == ["anime-offline", "anilist"]
    assert (result["job_id"], "failed") in job_runner.finished
