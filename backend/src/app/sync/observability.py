from __future__ import annotations

from datetime import UTC, datetime
from time import perf_counter
from typing import Any


def now_utc_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_log_payload(
    *,
    source: str,
    phase: str,
    status: str,
    job_id: str | None = None,
    processed_items: int | None = None,
    failed_items: int | None = None,
    duration_ms: int | None = None,
    error_code: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source": source,
        "phase": phase,
        "status": status,
        "job_id": job_id,
        "processed_items": 0 if processed_items is None else processed_items,
        "failed_items": 0 if failed_items is None else failed_items,
        "duration_ms": 0 if duration_ms is None else duration_ms,
    }
    if error_code is not None:
        payload["error_code"] = error_code
    payload.update(extra)
    return payload


def build_sync_job_error_payload(
    *,
    source: str,
    status: str,
    errors: list[dict[str, str]] | None = None,
    completed_sources: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "source": source,
        "status": status,
        "errors": errors or [],
        "completed_sources": completed_sources or [],
    }


def duration_ms_since(started_at: float) -> int:
    return int((perf_counter() - started_at) * 1000)
