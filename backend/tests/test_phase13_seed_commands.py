from __future__ import annotations

from uuid import uuid4

from typer.testing import CliRunner

from src.app.commands.seed import app


runner = CliRunner()


def test_seed_source_commands_exist_and_call_orchestrator(monkeypatch):
    called: list[str] = []

    async def _fake_run(*, source: str, **_: object) -> dict[str, object]:
        called.append(source)
        return {
            "job_id": str(uuid4()),
            "source": source,
            "status": "completed",
            "processed_items": 10,
            "failed_items": 0,
        }

    monkeypatch.setattr("src.app.commands.seed.run_seed_source", _fake_run)

    for source in ("anime-offline", "anilist", "mangadex", "jikan"):
        result = runner.invoke(app, [source])
        assert result.exit_code == 0
        assert source in result.stdout

    assert called == ["anime-offline", "anilist", "mangadex", "jikan"]


def test_seed_source_command_logs_structured_fields(monkeypatch, caplog):
    caplog.set_level("INFO")

    async def _fake_run(*, source: str, **_: object) -> dict[str, object]:
        return {
            "job_id": "9fc7f748-8126-4ddf-a8c2-593ed8f72db4",
            "source": source,
            "status": "partial",
            "processed_items": 5,
            "failed_items": 2,
        }

    monkeypatch.setattr("src.app.commands.seed.run_seed_source", _fake_run)

    result = runner.invoke(app, ["anilist"])

    assert result.exit_code == 0
    assert any(
        all(
            key in record.__dict__
            for key in ("source", "job_id", "status", "processed_items", "failed_items")
        )
        for record in caplog.records
    )


def test_seed_all_command_supports_dry_run_and_resume(monkeypatch):
    async def _fake_run_all(**kwargs: object) -> dict[str, object]:
        assert kwargs["dry_run"] is True
        assert kwargs["resume_job_id"] == "resume-123"
        return {
            "job_id": str(uuid4()),
            "source": "all",
            "status": "completed",
            "processed_items": 40,
            "failed_items": 0,
            "steps": [{"source": "anime-offline", "status": "completed"}],
            "dry_run": True,
            "resumed_from": "resume-123",
        }

    monkeypatch.setattr("src.app.commands.seed.run_seed_all", _fake_run_all)

    result = runner.invoke(app, ["all", "--dry-run", "--resume-job-id", "resume-123"])
    assert result.exit_code == 0
    assert "source=all" in result.stdout
    assert "dry_run=True" in result.stdout
