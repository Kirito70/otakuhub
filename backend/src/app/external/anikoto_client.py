"""Backend-only Anikoto catalog client (ADR 078).

This client stores/returns provider catalog and episode IDs only. It does not
scrape or fetch raw media segment URLs.

Rate-limit & stability behaviour
---------------------------------
* Maintains a conservative in-process token bucket (45 requests per 120 s).
* Reads ``X-RateLimit-Remaining`` / ``X-RateLimit-Reset`` response headers to
  dynamically tune the bucket when the server reports pressure.
* On 429 (rate limit) the caller receives ``AnikotoRateLimitError`` with the
  ``Retry-After`` duration.
* On 403 (transient ban from aggressive traffic) the request is retried with
  exponential backoff instead of immediately failing — the API docs note that
  *"very heavy or abusive traffic may get 403"*, implying it can be a temporary
  state.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from src.app.core.rate_limiter import RateLimiter

_logger = logging.getLogger(__name__)


class AnikotoClientError(RuntimeError):
    pass


class AnikotoForbiddenError(AnikotoClientError):
    pass


class AnikotoRateLimitError(AnikotoClientError):
    def __init__(self, retry_after: float) -> None:
        super().__init__(f"Anikoto rate limit exceeded; retry after {retry_after}s")
        self.retry_after = retry_after


class AnikotoClient:
    """Rate-limited async HTTP client for documented Anikoto endpoints.

    Parameters
    ----------
    base_url:
        Anikoto API base URL.
    timeout:
        Per-request timeout in seconds.
    max_retries:
        Number of retries for transient errors (transport, 5xx, 403).
    rate_max:
        Maximum requests per ``rate_window`` seconds.
    rate_window:
        Sliding window for the token bucket in seconds.
    http_client:
        Optional pre-configured ``httpx.AsyncClient`` (useful for tests).
    """

    def __init__(
        self,
        *,
        base_url: str = "https://anikotoapi.site",
        timeout: float = 10.0,
        max_retries: int = 2,
        rate_max: int = 45,
        rate_window: float = 120.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limiter = RateLimiter(max_requests=rate_max, time_window=rate_window)
        self._client = http_client

    async def get_recent_anime(self, *, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        return await self._get("/recent-anime", params={"page": page, "per_page": per_page})

    async def get_series(self, series_id: str) -> dict[str, Any]:
        safe_id = str(series_id).strip().strip("/")
        return await self._get(f"/series/{safe_id}")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            await self.rate_limiter.acquire()
            try:
                client = self._client or httpx.AsyncClient(timeout=self.timeout)
                close_client = self._client is None
                try:
                    response = await client.get(f"{self.base_url}{path}", params=params)
                    self._adapt_rate_limit_from_headers(response)
                finally:
                    if close_client:
                        await client.aclose()

                if response.status_code == 429:
                    retry_after = self._retry_after_seconds(response)
                    raise AnikotoRateLimitError(retry_after)

                if response.status_code == 403:
                    _logger.warning("Anikoto 403 (attempt %d/%d) — may be transient", attempt + 1, self.max_retries + 1)
                    if attempt >= self.max_retries:
                        raise AnikotoForbiddenError("Anikoto returned 403 Forbidden — all retries exhausted")
                    await asyncio.sleep(2**attempt * 5)
                    continue

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

    def _adapt_rate_limit_from_headers(self, response: httpx.Response) -> None:
        """Dynamically tune the token bucket using ``X-RateLimit-*`` headers.

        When the server reports fewer remaining tokens than our configured
        bucket size, we reduce our bucket to match so we don't over-send in
        the next window.
        """
        remaining_str = response.headers.get("X-RateLimit-Remaining")
        reset_str = response.headers.get("X-RateLimit-Reset")
        if remaining_str is not None and reset_str is not None:
            try:
                remaining = int(remaining_str)
                reset_in = float(reset_str)
                if remaining < self.rate_limiter.max_requests and reset_in > 0:
                    # Server has fewer tokens left than our bucket — tighten.
                    new_max = max(remaining - 2, 2)  # leave a small safety margin
                    _logger.debug("Anikoto X-RateLimit-Remaining=%d; adjusting bucket %d → %d", remaining, self.rate_limiter.max_requests, new_max)
                    self.rate_limiter.max_requests = new_max
            except (ValueError, TypeError):
                pass
