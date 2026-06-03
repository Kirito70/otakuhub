from __future__ import annotations

from src.app.sync.job_runner import sanitize_error_message
from src.app.sync.observability import build_sync_job_error_payload


def test_sanitize_error_message_redacts_tokens_and_secrets():
    raw = "failed with token=abc123 secret=my-secret password=hunter2"
    sanitized = sanitize_error_message(raw)

    assert "abc123" not in sanitized
    assert "my-secret" not in sanitized
    assert "hunter2" not in sanitized
    assert "[REDACTED]" in sanitized


def test_sync_job_error_payload_shape_is_standardized():
    payload = build_sync_job_error_payload(
        source="all",
        status="partial",
        errors=[{"item": "job-1", "source": "anilist", "error": "boom"}],
        completed_sources=["anime-offline"],
    )

    assert set(payload.keys()) == {"source", "status", "errors", "completed_sources"}
    assert payload["source"] == "all"
    assert payload["status"] == "partial"
