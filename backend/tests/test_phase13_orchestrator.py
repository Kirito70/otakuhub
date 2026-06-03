from __future__ import annotations

import logging

import pytest

from src.app.sync.orchestrator import SeedOrchestrator
from src.app.sync.types import SeedExecutionContext, SeedRunResult


class _FakeRunner:
    def __init__(self) -> None:
        self.started = False
        self.progressed = False
        self.finished_status: str | None = None

    async def start_job(self, *, source: str, total_items: int | None = None, user_id: str | None = None):
        self.started = True
        return "job-1"

    async def progress(self, *, job_id: str, processed_items: int, failed_items: int):
        self.progressed = True

    async def finish_completed(self, *, job_id: str, source: str = "unknown"):
        self.finished_status = "completed"

    async def finish_partial(self, *, job_id: str, errors, source: str = "unknown"):
        self.finished_status = "partial"

    async def finish_failed(self, *, job_id: str, errors, source: str = "unknown"):
        self.finished_status = "failed"


class _OkAdapter:
    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        return SeedRunResult(source=context.source, status="completed", processed_items=12, failed_items=0, errors=[])


class _PartialAdapter:
    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        return SeedRunResult(source=context.source, status="partial", processed_items=5, failed_items=2, errors=[{"item": "1", "source": context.source, "error": "bad"}])


@pytest.mark.asyncio
async def test_orchestrator_updates_sync_job_lifecycle_completed():
    runner = _FakeRunner()
    orchestrator = SeedOrchestrator(job_runner=runner, adapters={"anilist": _OkAdapter()})

    result = await orchestrator.run_source(source="anilist")

    assert result["status"] == "completed"
    assert runner.started is True
    assert runner.progressed is True
    assert runner.finished_status == "completed"


@pytest.mark.asyncio
async def test_orchestrator_updates_sync_job_lifecycle_partial():
    runner = _FakeRunner()
    orchestrator = SeedOrchestrator(job_runner=runner, adapters={"jikan": _PartialAdapter()})

    result = await orchestrator.run_source(source="jikan")

    assert result["status"] == "partial"
    assert runner.finished_status == "partial"


@pytest.mark.asyncio
async def test_orchestrator_logs_standardized_observability_fields(caplog):
    caplog.set_level(logging.INFO)
    runner = _FakeRunner()
    orchestrator = SeedOrchestrator(job_runner=runner, adapters={"anilist": _OkAdapter()})

    await orchestrator.run_source(source="anilist")

    assert any(
        all(
            key in record.__dict__
            for key in (
                "source",
                "job_id",
                "phase",
                "status",
                "processed_items",
                "failed_items",
                "duration_ms",
            )
        )
        for record in caplog.records
    )
