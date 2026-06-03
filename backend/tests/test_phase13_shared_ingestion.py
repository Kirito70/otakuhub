from __future__ import annotations

import pytest

from src.app.sync.ingestion import IngestionRetryPolicy, run_ingestion
from src.app.sync.types import SeedExecutionContext


@pytest.mark.asyncio
async def test_run_ingestion_retries_retryable_failures_then_succeeds():
    attempts = {"count": 0}

    async def _parse(item_index: int) -> dict[str, int]:
        return {"i": item_index}

    async def _upsert(_: dict[str, int]) -> None:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("transient")

    context = SeedExecutionContext(source="anilist", job_id="job-1", limit=1)

    result = await run_ingestion(
        context=context,
        item_count=1,
        parse_item=_parse,
        upsert_item=_upsert,
        retry_policy=IngestionRetryPolicy(max_attempts=2),
    )

    assert result.status == "completed"
    assert result.processed_items == 1
    assert result.failed_items == 0
    assert attempts["count"] == 2


@pytest.mark.asyncio
async def test_run_ingestion_marks_partial_for_non_retryable_error():
    async def _parse(_: int) -> dict[str, int]:
        raise ValueError("bad payload")

    async def _upsert(_: dict[str, int]) -> None:
        return None

    context = SeedExecutionContext(source="jikan", job_id="job-2", limit=1)

    result = await run_ingestion(
        context=context,
        item_count=1,
        parse_item=_parse,
        upsert_item=_upsert,
        retry_policy=IngestionRetryPolicy(max_attempts=3),
    )

    assert result.status == "partial"
    assert result.processed_items == 0
    assert result.failed_items == 1
    assert result.errors[0]["source"] == "jikan"
