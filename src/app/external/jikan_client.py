"""Jikan API client for MyAnimeList supplemental data."""

import aiohttp
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from src.app.core.rate_limiter import RateLimiter


class JikanClient:
    """Jikan API client with rate limiting."""

    def __init__(self):
        self.base_url = "https://api.jikan.moe/v4/"
        self.session = None
        self.rate_limiter = RateLimiter(max_requests=1, time_window=1)  # 1 request per second

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def _make_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make a request to the Jikan API with rate limiting."""
        if not self.session:
            raise Exception("Client not initialized. Use async with context manager.")

        await self.rate_limiter.acquire()

        url = urljoin(self.base_url, endpoint)
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Jikan API error {response.status}: {await response.text()}")
                    return None
        except Exception as e:
            print(f"Jikan API request failed: {e}")
            return None

    async def search_anime(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for anime."""
        endpoint = f"anime?q={query}&limit={limit}"
        result = await self._make_request(endpoint)
        return result.get("data", []) if result else []

    async def get_anime_details(self, anime_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed anime information."""
        endpoint = f"anime/{anime_id}"
        result = await self._make_request(endpoint)
        return result.get("data") if result else None
