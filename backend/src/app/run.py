"""Entrypoint helpers for local uv-based development."""

from __future__ import annotations

import uvicorn


def main() -> None:
    """Run FastAPI app with sensible local defaults."""
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
