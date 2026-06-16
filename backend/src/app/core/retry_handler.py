"""Shared retry handler for external API rate limits and transient errors.

Provides utilities for all external API clients (AniList, MangaDex, Jikan):
- ``retry_on_429`` — decorator for async functions that retries on 429/5xx
  with ``Retry-After`` header support and exponential backoff + jitter.
"""

from __future__ import annotations

import asyncio
import random
import logging
from typing import Any, Callable, Coroutine, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_on_rate_limit(
    coro_factory: Callable[[], Coroutine[Any, Any, T]],
    *,
    max_retries: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 120.0,
    jitter: float = 0.1,
    retryable_statuses: tuple[int, ...] = (429, 502, 503, 504),
    is_rate_limited_fn: Callable[[Exception], tuple[bool, float | None]] | None = None,
) -> T:
    """Execute an async call with retry logic for rate limits and server errors.

    Args:
        coro_factory: Async callable that returns the desired result.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds before first retry.
        max_delay: Maximum delay in seconds between retries.
        jitter: Random jitter factor (0.1 = ±10%).
        retryable_statuses: HTTP status codes that trigger a retry.
        is_rate_limited_fn: Optional function that examines an exception and
            returns (is_rate_limited, retry_after_seconds). If *retry_after* is
            provided by the API (``Retry-After`` header), it takes precedence
            over exponential backoff.

    Returns:
        The result of the coroutine on success.

    Raises:
        The last exception if all retries are exhausted.
    """
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await coro_factory()
        except Exception as exc:
            last_exc = exc

            # Determine if we should retry and how long to wait
            retry_after: float | None = None
            should_retry = False

            if is_rate_limited_fn:
                is_rl, retry_after = is_rate_limited_fn(exc)
                should_retry = is_rl

            if not should_retry:
                # Check for typical rate-limit patterns in the error
                exc_str = str(exc).lower()
                if any(
                    pattern in exc_str
                    for pattern in ["429", "too many requests", "rate limit"]
                ):
                    should_retry = True
                    # Try to extract a delay from the error message
                    if retry_after is None:
                        import re

                        match = re.search(r"retry.after[:\s]+(\d+)", exc_str, re.IGNORECASE)
                        if match:
                            retry_after = float(match.group(1))

            if not should_retry or attempt >= max_retries:
                raise  # Re-raise the last exception

            # Calculate delay: prefer Retry-After, fall back to exponential backoff
            if retry_after is not None:
                delay = min(float(retry_after), max_delay)
            else:
                delay = min(base_delay * (2**attempt), max_delay)

            # Add jitter
            delay *= 1.0 + random.uniform(-jitter, jitter)

            logger.warning(
                "rate_limit_retry",
                extra={
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "delay_seconds": round(delay, 1),
                    "error": str(exc)[:200],
                },
            )
            await asyncio.sleep(delay)

    # Should not reach here, but belt-and-suspenders
    raise last_exc  # type: ignore[misc]
