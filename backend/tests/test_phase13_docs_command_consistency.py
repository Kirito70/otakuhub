from __future__ import annotations

from pathlib import Path


def test_phase13_runtime_docs_use_canonical_otakuhub_seed_commands() -> None:
    """Phase 13 runtime docs should point to canonical CLI paths only."""
    repo_root = Path(__file__).resolve().parents[2]

    runtime_docs = [
        repo_root / "backend" / "README.md",
        repo_root / "docs" / "sync-pipeline.md",
    ]

    for doc_path in runtime_docs:
        content = doc_path.read_text(encoding="utf-8")
        assert "uv run otakuhub seed anime-offline" in content
        assert "uv run otakuhub seed all" in content
        assert "uv run otakuhub seed run" not in content


def test_sync_pipeline_beat_task_examples_use_sync_task_names() -> None:
    """Beat schedule examples should align with canonical Celery task names."""
    repo_root = Path(__file__).resolve().parents[2]
    content = (repo_root / "docs" / "sync-pipeline.md").read_text(encoding="utf-8")

    assert "workers.sync_tasks.weekly_refresh" not in content
    assert "workers.sync_tasks.refresh_airing_schedule" not in content
    assert "sync.weekly_refresh" in content
