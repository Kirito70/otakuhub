"""Phase 23.4 performance checks."""

from __future__ import annotations

import statistics
import time
from types import SimpleNamespace

from fastapi.testclient import TestClient

from src.app.main import app
from src.app.routes.media import get_media_service
from src.app.core.auth import get_current_user


class FastMediaService:
    async def search_media(self, **_kwargs):
        return []


def _override_current_user() -> SimpleNamespace:
    return SimpleNamespace(id="perf-user")


def test_media_search_p95_under_200ms() -> None:
    app.dependency_overrides[get_current_user] = _override_current_user
    app.dependency_overrides[get_media_service] = lambda: FastMediaService()

    try:
        with TestClient(app) as client:
            # warm-up
            for _ in range(10):
                resp = client.get("/api/v1/media/search", params={"query": "naruto", "limit": 20, "offset": 0})
                assert resp.status_code == 200, resp.text

            samples_ms: list[float] = []
            for _ in range(60):
                start = time.perf_counter()
                resp = client.get("/api/v1/media/search", params={"query": "naruto", "limit": 20, "offset": 0})
                elapsed_ms = (time.perf_counter() - start) * 1000
                assert resp.status_code == 200, resp.text
                samples_ms.append(elapsed_ms)

            p95_ms = statistics.quantiles(samples_ms, n=100, method="inclusive")[94]
            assert p95_ms < 200, f"Expected p95 < 200ms, got {p95_ms:.2f}ms"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_media_service, None)
