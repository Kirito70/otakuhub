"""Data seeding commands."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer

app = typer.Typer(name="seed", help="Data seed commands")


@app.command("run")
def run_seed_script() -> None:
    """Run the local seed script directly (non-Celery)."""
    root = Path(__file__).resolve().parents[4]
    script_path = root / "scripts" / "seed_database.py"

    if not script_path.exists():
        typer.echo("✗ scripts/seed_database.py not found")
        raise typer.Exit(1)

    namespace: dict[str, object] = {}
    exec(script_path.read_text(encoding="utf-8"), namespace)
    seed_func = namespace.get("seed_database")

    if seed_func is None:
        typer.echo("✗ seed_database() function not found in script")
        raise typer.Exit(1)

    typer.echo("Running seed script...")
    asyncio.run(seed_func())
    typer.echo("✓ Seed script finished")
