"""Backend-only Anikoto catalog client (ADR 078).

This client stores/returns provider catalog and episode IDs only. It does not
scrape or fetch raw media segment URLs.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from src.app.core.rate_limiter import RateLimiter


class AnikotoClientError(RuntimeError):
    pass


class AnikotoForbiddenError(AnikotoClientError):
    pass


class AnikotoRateLimitError(AnikotoClientError):
    def __init__(self, retry_after: float) -> None:
        super().__init__(f"Anikoto rate limit exceeded; retry after {retry_after}s")
        self.retry_after = retry_after


class AnikotoClient:
    """Rate-limited async HTTP client for documented Anikoto endpoints."""

    def __init__(
        self,
        *,
        base_url: str = "https://anikotoapi.site",
        timeout: float = 10.0,
        max_retries: int = 2,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(max_requests=45, time_window=120.0)
        self._client = http_client

    async def get_recent_anime(self, *, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        return await self._get("/recent-anime", params={"page": page, "per_page": per_page})

    async def get_series(self, series_id: str) -> dict[str, Any]:
        safe_id = str(series_id).strip().strip("/")
        return await self._get(f"/series/{safe_id}")

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            await self.rate_limiter.acquire()
            try:
                client = self._client or httpx.AsyncClient(timeout=self.timeout)
                close_client = self._client is None
                try:
                    response = await client.get(f"{self.base_url}{path}", params=params)
                finally:
                    if close_client:
                        await client.aclose()

                if response.status_code == 403:
                    raise AnikotoForbiddenError("Anikoto returned 403 Forbidden")
                if response.status_code == 429:
                    retry_after = self._retry_after_seconds(response)
                    raise AnikotoRateLimitError(retry_after)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    return {"items": data}
                return data
            except AnikotoRateLimitError:
                raise
            except AnikotoForbiddenError:
                raise
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                if attempt >= self.max_retries:
                    break
                await asyncio.sleep(2**attempt)
        raise AnikotoClientError(str(last_exc) if last_exc else "Anikoto request failed")

    @staticmethod
    def _retry_after_seconds(response: httpx.Response) -> float:
        raw = response.headers.get("Retry-After") or response.headers.get("retry-after")
        if raw:
            try:
                return max(float(raw), 1.0)
            except ValueError:
                return 30.0
        return 30.0
