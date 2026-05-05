"""CLI entrypoint for OtakuHub backend commands."""

from __future__ import annotations

from src.app.commands import app


def main() -> None:
    """Run Typer CLI app."""
    app()
