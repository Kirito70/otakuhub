from __future__ import annotations

import importlib.util
from pathlib import Path

from typer.testing import CliRunner

from src.app.commands.seed import app as seed_app


runner = CliRunner()


def _load_root_seed_script_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "seed_database.py"
    spec = importlib.util.spec_from_file_location("deprecated_seed_script", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_seed_run_command_is_deprecated_but_supported(monkeypatch):
    async def _fake_run(*, source: str, **_: object) -> dict[str, object]:
        assert source == "anime-offline"
        return {
            "job_id": "job-1",
            "source": source,
            "status": "completed",
            "processed_items": 1,
            "failed_items": 0,
        }

    monkeypatch.setattr("src.app.commands.seed.run_seed_source", _fake_run)

    result = runner.invoke(seed_app, ["run"])

    assert result.exit_code == 0
    assert "DEPRECATED" in result.stdout
    assert "otakuhub seed anime-offline" in result.stdout


def test_root_seed_script_emits_deprecation_and_invokes_backend_orchestrator(monkeypatch, capsys):
    module = _load_root_seed_script_module()

    async def _fake_run(*, source: str, **_: object) -> dict[str, object]:
        assert source == "anime-offline"
        return {
            "job_id": "job-2",
            "source": source,
            "status": "completed",
            "processed_items": 12,
            "failed_items": 0,
        }

    monkeypatch.setattr(module, "run_seed_source", _fake_run)

    exit_code = module.main()

    output = capsys.readouterr().out
    assert exit_code == 0
    assert "DEPRECATED" in output
    assert "otakuhub seed anime-offline" in output
    assert "source=anime-offline" in output
