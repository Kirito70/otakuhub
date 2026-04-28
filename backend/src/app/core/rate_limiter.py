"""Simple rate limiter stub for testing.

The real implementation would enforce request limits, but for unit tests we only need
an async ``acquire`` method that returns immediately.
"""

import asyncio


class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        # No actual limiting logic – placeholder

    async def acquire(self):
        # In production this would wait until a token is available.
        # For tests we simply pass.
        await asyncio.sleep(0)
