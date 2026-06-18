"""Sliding-window rate limiter for external API calls.

Maintains a per-instance list of request timestamps and blocks (via
``asyncio.sleep``) when the window is full.  Designed for single-worker
Celery sync processes — NOT Redis-backed / multi-worker safe.

Supports temporary server-enforced caps::

    limiter = RateLimiter(max_requests=60, time_window=60.0, min_requests=10)
    # Server says: 20 remaining, reset at Unix timestamp T
    limiter.set_server_cap(remaining=20, reset_in_seconds=45.0)
    # For the next 45 seconds, max_requests is capped at max(20-2, 10) = 18
    # After 45s elapses, max_requests restores to the base of 60
"""

from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """In-memory sliding-window rate limiter.

    Parameters
    ----------
    max_requests:
        Maximum requests allowed in the sliding window.
    time_window:
        Sliding window duration in seconds.
    min_requests:
        Floor for server-cap adaptations — never cap below this value.
    """

    def __init__(
        self,
        max_requests: int = 100,
        time_window: float = 60.0,
        min_requests: int = 10,
    ) -> None:
        self.base_max_requests = max_requests
        self.max_requests = max_requests
        self.time_window = time_window
        self.min_requests = min_requests
        self._timestamps: list[float] = []
        # Server-cap tracking: (capped_max, expires_at_monotonic)
        self._server_cap: tuple[int, float] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def acquire(self) -> None:
        """Block until a rate-limit slot is available, then record the request."""
        now = time.monotonic()
        # Check whether a temporary server cap has expired
        self._maybe_restore_base(now)
        # Prune timestamps outside the current window
        cutoff = now - self.time_window
        self._timestamps = [t for t in self._timestamps if t > cutoff]

        if len(self._timestamps) >= self.max_requests:
            # Sleep until the oldest timestamp expires
            sleep_for = self._timestamps[0] + self.time_window - now
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            now = time.monotonic()
            self._maybe_restore_base(now)
            # Prune again after sleeping
            cutoff = now - self.time_window
            self._timestamps = [t for t in self._timestamps if t > cutoff]

        self._timestamps.append(time.monotonic())

    def set_server_cap(self, remaining: int, reset_in_seconds: float) -> None:
        """Temporarily lower ``max_requests`` based on a server-enforced cap.

        The cap expires after ``reset_in_seconds``, after which
        ``max_requests`` restores to the base value.

        Parameters
        ----------
        remaining:
            ``X-RateLimit-Remaining`` from the server (current capacity).
        reset_in_seconds:
            Seconds until the server's rate-limit window resets
            (derived from ``X-RateLimit-Reset`` Unix timestamp).
        """
        if remaining <= 0:
            new_max = self.min_requests
        else:
            # Leave a small safety margin so we don't slam the reset
            new_max = max(remaining - 2, self.min_requests)

        if new_max < self.max_requests:
            expires_at = time.monotonic() + max(reset_in_seconds, 0)
            self.max_requests = new_max
            self._server_cap = (new_max, expires_at)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _maybe_restore_base(self, now: float) -> None:
        """If a server cap has expired, restore the base ``max_requests``."""
        if self._server_cap is not None:
            _, expires_at = self._server_cap
            if now >= expires_at:
                self.max_requests = self.base_max_requests
                self._server_cap = None
