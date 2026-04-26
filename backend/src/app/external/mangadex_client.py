"""MangaDex API client."""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from src.app.core.rate_limiter import RateLimiter


class MangaDexClient:
    """MangaDex API client with rate limiting."""
    
    def __init__(self):
        self.base_url = "https://api.mangadex.org/"
        self.session = None
        self.rate_limiter = RateLimiter(max_requests=10, time_window=1)  # 10 requests per second
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _make_request(self, endpoint: str, method: str = "GET", 
                          data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make a request to the MangaDex API with rate limiting."""
        if not self.session:
            raise Exception("Client not initialized. Use async with context manager.")
            
        await self.rate_limiter.acquire()
        
        url = urljoin(self.base_url, endpoint)
        try:
            if method == "GET":
                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"MangaDex API error {response.status}: {await response.text()}")
                        return None
            elif method == "POST":
                async with self.session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"MangaDex API error {response.status}: {await response.text()}")
                        return None
        except Exception as e:
            print(f"MangaDex API request failed: {e}")
            return None
    
    async def get_manga_details(self, manga_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed manga information."""
        endpoint = f"manga/{manga_id}"
        result = await self._make_request(endpoint)
        return result.get("data") if result else None
    
    async def get_chapters(self, manga_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get manga chapters."""
        endpoint = f"manga/{manga_id}/feed"
        params = {"limit": limit}
        # You'd need to add query parameters here
        result = await self._make_request(endpoint)
        return result.get("data", []) if result else []
    
    async def get_manga_list(self, title: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for manga by title."""
        endpoint = "manga"
        # This would need correct parameter handling for the API
        result = await self._make_request(endpoint)
        return result.get("data", []) if result else []