"""Jikan API client (MyAnimeList supplemental data).

Uses a lazy ``aiohttp.ClientSession`` so the client can be used directly
without requiring an ``async with`` context manager.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

from src.app.core.rate_limiter import RateLimiter


class JikanClient:
    """Jikan (MyAnimeList v4) API client with rate limiting.

    Usage::

        client = JikanClient()
        anime = await client.search_anime("Naruto")
    """

    def __init__(self) -> None:
        self.base_url = "https://api.jikan.moe/v4/"
        self._session: aiohttp.ClientSession | None = None
        self.rate_limiter = RateLimiter(max_requests=1, time_window=1.0)

    # ------------------------------------------------------------------
    # Lazy session
    # ------------------------------------------------------------------

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def __aenter__(self) -> "JikanClient":
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    # ------------------------------------------------------------------
    # Internal request helper
    # ------------------------------------------------------------------

    async def _make_request(
        self, endpoint: str
    ) -> Optional[Dict[str, Any]]:
        """Make a rate-limited GET request to the Jikan API."""
        await self.rate_limiter.acquire()

        url = urljoin(self.base_url, endpoint)
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                print(
                    f"Jikan API error {response.status}: {await response.text()}"
                )
                return None
        except Exception as e:
            print(f"Jikan API request failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def search_anime(
        self, query: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for anime by title."""
        endpoint = f"anime?q={query}&limit={limit}"
        result = await self._make_request(endpoint)
        return result.get("data", []) if result else []

    async def search_manga(
        self, query: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for manga by title."""
        endpoint = f"manga?q={query}&limit={limit}"
        result = await self._make_request(endpoint)
        return result.get("data", []) if result else []

    async def get_anime_details(
        self, anime_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get detailed anime information by MAL ID."""
        endpoint = f"anime/{anime_id}"
        result = await self._make_request(endpoint)
        return result.get("data") if result else None

    async def get_manga_details(
        self, manga_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get detailed manga information by MAL ID."""
        endpoint = f"manga/{manga_id}"
        result = await self._make_request(endpoint)
        return result.get("data") if result else None
