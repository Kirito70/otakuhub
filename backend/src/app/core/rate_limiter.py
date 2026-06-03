"""Sliding-window rate limiter for external API calls.

Maintains a per-instance list of request timestamps and blocks (via
``asyncio.sleep``) when the window is full.  Designed for single-worker
Celery sync processes — NOT Redis-backed / multi-worker safe.
"""

from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """In-memory sliding-window rate limiter.

    Example::

        limiter = RateLimiter(max_requests=80, time_window=60.0)
        await limiter.acquire()   # may sleep if window is full
        await do_api_call()
    """

    def __init__(self, max_requests: int = 100, time_window: float = 60.0) -> None:
        self.max_requests = max_requests
        self.time_window = time_window
        self._timestamps: list[float] = []

    async def acquire(self) -> None:
        """Block until a rate-limit slot is available, then record the request."""
        now = time.monotonic()
        # Prune timestamps outside the current window
        cutoff = now - self.time_window
        self._timestamps = [t for t in self._timestamps if t > cutoff]

        if len(self._timestamps) >= self.max_requests:
            # Sleep until the oldest timestamp expires
            sleep_for = self._timestamps[0] + self.time_window - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            now = time.monotonic()
            # Prune again after sleeping
            cutoff = now - self.time_window
            self._timestamps = [t for t in self._timestamps if t > cutoff]

        self._timestamps.append(time.monotonic())
