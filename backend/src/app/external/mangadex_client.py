"""MangaDex API client with rate limiting.

Uses a lazy ``aiohttp.ClientSession`` so the client can be instantiated
directly (without ``async with``) while still supporting explicit context
manager usage for backward compatibility.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import aiohttp

from src.app.core.rate_limiter import RateLimiter


class MangaDexClient:
    """MangaDex REST API client.

    Usage (preferred — no context manager needed)::

        client = MangaDexClient()
        details = await client.get_manga_details("uuid")

    Backward-compatible context-manager usage is also supported::

        async with MangaDexClient() as client:
            details = await client.get_manga_details("uuid")
    """

    def __init__(self) -> None:
        self.base_url = "https://api.mangadex.org/"
        self._session: aiohttp.ClientSession | None = None
        self.rate_limiter = RateLimiter(max_requests=4, time_window=1.0)

    # ------------------------------------------------------------------
    # Lazy session
    # ------------------------------------------------------------------

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def __aenter__(self) -> "MangaDexClient":
        # Explicitly create the session for context-manager usage
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
        self,
        endpoint: str,
        method: str = "GET",
        params: Dict[str, Any] | None = None,
        data: Dict[str, Any] | None = None,
    ) -> Optional[Dict[str, Any]]:
        """Make a rate-limited HTTP request to the MangaDex API."""
        await self.rate_limiter.acquire()

        url = urljoin(self.base_url, endpoint)
        try:
            if method == "GET":
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    print(
                        f"MangaDex API error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    print(
                        f"MangaDex API error {response.status}: "
                        f"{await response.text()}"
                    )
                    return None
        except Exception as e:
            print(f"MangaDex API request failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------------

    async def get_manga_details(self, manga_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed manga information by MangaDex UUID."""
        endpoint = f"manga/{manga_id}"
        result = await self._make_request(endpoint)
        return result.get("data") if result else None

    async def get_chapters(
        self, manga_id: str, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get chapters for a manga.

        Args:
            manga_id: MangaDex UUID of the manga.
            limit: Number of chapters to return (max 500).
            offset: Pagination offset.

        Returns:
            List of chapter data dicts from the API response.
        """
        endpoint = f"manga/{manga_id}/feed"
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "translatedLanguage[]": "en",
            "order[chapter]": "asc",
        }
        result = await self._make_request(endpoint, params=params)
        return result.get("data", []) if result else []

    async def get_manga_list(
        self, title: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for manga by title.

        Uses the MangaDex v5 ``GET /manga?title=`` endpoint.
        """
        endpoint = "manga"
        params: Dict[str, Any] = {
            "title": title,
            "limit": limit,
        }
        result = await self._make_request(endpoint, params=params)
        return result.get("data", []) if result else []
