from __future__ import annotations

import logging
from time import perf_counter

from src.app.sync.observability import build_log_payload, duration_ms_since
from src.app.sync.types import SeedExecutionContext, SeedSourceAdapter

logger = logging.getLogger(__name__)


class SeedOrchestrator:
    def __init__(self, job_runner, adapters: dict[str, SeedSourceAdapter]):
        self.job_runner = job_runner
        self.adapters = adapters

    async def run_source(self, *, source: str, **kwargs: object) -> dict[str, object]:
        user_id = kwargs.get("user_id")
        adapter = self.adapters[source]
        job_id = await self.job_runner.start_job(
            source=source,
            total_items=kwargs.get("limit"),
            user_id=user_id,
        )
        context = SeedExecutionContext(
            source=source,
            job_id=job_id,
            dry_run=bool(kwargs.get("dry_run", False)),
            limit=kwargs.get("limit"),
            batch_size=kwargs.get("batch_size"),
            only_unsynced=bool(kwargs.get("only_unsynced", False)),
            user_id=user_id,
        )
        started_at = perf_counter()
        try:
            result = await adapter.run(context)
            await self.job_runner.progress(
                job_id=job_id,
                processed_items=result.processed_items,
                failed_items=result.failed_items,
            )
            if result.status == "completed":
                await self.job_runner.finish_completed(job_id=job_id, source=source)
            elif result.status == "partial":
                await self.job_runner.finish_partial(job_id=job_id, errors=result.errors, source=source)
            else:
                await self.job_runner.finish_failed(job_id=job_id, errors=result.errors, source=source)

            payload = build_log_payload(
                source=source,
                phase="orchestrator",
                job_id=job_id,
                status=result.status,
                processed_items=result.processed_items,
                failed_items=result.failed_items,
                duration_ms=duration_ms_since(started_at),
            )
            logger.info("seed_orchestration_finished", extra=payload)
            return payload
        except Exception as exc:
            errors = [{"item": "command", "source": source, "error": str(exc)}]
            await self.job_runner.finish_failed(job_id=job_id, errors=errors, source=source)
            logger.error(
                "seed_orchestration_failed",
                extra=build_log_payload(
                    source=source,
                    phase="orchestrator",
                    job_id=job_id,
                    status="failed",
                    processed_items=0,
                    failed_items=1,
                    duration_ms=duration_ms_since(started_at),
                    error_code="ORCHESTRATION_EXCEPTION",
                ),
            )
            raise

    async def run_all(
        self,
        *,
        dry_run: bool = False,
        resume_job_id: str | None = None,
        batch_size: int | None = None,
        limit: int | None = None,
        user_id: str | None = None,
    ) -> dict[str, object]:
        order = ["anime-offline", "anilist", "mangadex", "jikan"]
        completed_sources: set[str] = set()

        if resume_job_id:
            completed_sources = set(await self.job_runner.get_completed_sources_for_resume(job_id=resume_job_id))

        umbrella_job_id = await self.job_runner.start_job(source="all", total_items=None, user_id=user_id)
        step_results: list[dict[str, object]] = []

        try:
            for source in order:
                if source in completed_sources:
                    step_results.append(
                        {
                            "source": source,
                            "status": "skipped",
                            "processed_items": 0,
                            "failed_items": 0,
                            "resumed": True,
                        }
                    )
                    continue

                source_result = await self.run_source(
                    source=source,
                    dry_run=dry_run,
                    batch_size=batch_size if source == "anime-offline" else None,
                    limit=limit if source != "anime-offline" else None,
                    only_unsynced=False,
                    user_id=user_id,
                )
                step_results.append(source_result)

                if source_result["status"] != "completed":
                    break

            failed_steps = [step for step in step_results if step["status"] == "failed"]
            partial_steps = [step for step in step_results if step["status"] == "partial"]

            processed_total = sum(int(step.get("processed_items", 0)) for step in step_results)
            failed_total = sum(int(step.get("failed_items", 0)) for step in step_results)

            if failed_steps:
                errors = [
                    {
                        "item": str(step.get("job_id", "unknown")),
                        "source": str(step["source"]),
                        "error": "source step failed during seed all",
                    }
                    for step in failed_steps
                ]
                await self.job_runner.progress(
                    job_id=umbrella_job_id,
                    processed_items=processed_total,
                    failed_items=failed_total,
                )
                await self.job_runner.finish_failed(job_id=umbrella_job_id, errors=errors, source="all")
                overall_status = "failed"
            elif partial_steps:
                errors = [
                    {
                        "item": str(step.get("job_id", "unknown")),
                        "source": str(step["source"]),
                        "error": "source step partial during seed all",
                    }
                    for step in partial_steps
                ]
                await self.job_runner.progress(
                    job_id=umbrella_job_id,
                    processed_items=processed_total,
                    failed_items=failed_total,
                )
                await self.job_runner.finish_partial(job_id=umbrella_job_id, errors=errors, source="all")
                overall_status = "partial"
            else:
                resume_payload = [step["source"] for step in step_results if step.get("status") in {"completed", "skipped"}]
                await self.job_runner.progress(
                    job_id=umbrella_job_id,
                    processed_items=processed_total,
                    failed_items=failed_total,
                )
                await self.job_runner.finish_completed(job_id=umbrella_job_id, source="all", resume_sources=resume_payload)
                overall_status = "completed"

            return {
                "source": "all",
                "job_id": umbrella_job_id,
                "status": overall_status,
                "processed_items": processed_total,
                "failed_items": failed_total,
                "steps": step_results,
                "dry_run": dry_run,
                "resumed_from": resume_job_id,
            }
        except Exception as exc:
            await self.job_runner.finish_failed(
                job_id=umbrella_job_id,
                errors=[{"item": "command", "source": "all", "error": str(exc)}],
                source="all",
            )
            raise
