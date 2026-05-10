from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

from src.app.sync.types import SeedExecutionContext, SeedRunResult

TItem = TypeVar("TItem")


@dataclass(slots=True)
class IngestionRetryPolicy:
    max_attempts: int = 3
    retryable_exceptions: tuple[type[Exception], ...] = (RuntimeError, TimeoutError, ConnectionError)


async def _with_retry(
    func: Callable[[], Awaitable[TItem]],
    *,
    retry_policy: IngestionRetryPolicy,
) -> TItem:
    attempts = 0
    while True:
        attempts += 1
        try:
            return await func()
        except retry_policy.retryable_exceptions:
            if attempts >= retry_policy.max_attempts:
                raise


async def run_ingestion(
    *,
    context: SeedExecutionContext,
    item_count: int,
    parse_item: Callable[[int], Awaitable[TItem]],
    upsert_item: Callable[[TItem], Awaitable[None]],
    retry_policy: IngestionRetryPolicy,
) -> SeedRunResult:
    processed = 0
    failed = 0
    errors: list[dict[str, str]] = []

    if context.dry_run:
        return SeedRunResult(
            source=context.source,
            status="completed",
            processed_items=item_count,
            failed_items=0,
            errors=[],
        )

    for item_index in range(item_count):
        try:
            parsed = await _with_retry(lambda: parse_item(item_index), retry_policy=retry_policy)
            await _with_retry(lambda: upsert_item(parsed), retry_policy=retry_policy)
            processed += 1
        except Exception as exc:
            failed += 1
            errors.append({"item": str(item_index), "source": context.source, "error": str(exc)})

    status = "completed" if failed == 0 else "partial"
    return SeedRunResult(
        source=context.source,
        status=status,
        processed_items=processed,
        failed_items=failed,
        errors=errors,
    )
