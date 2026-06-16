"""AniList GraphQL client with rate limiting and 429 retry.

AniList API rate limit: 90 requests per minute per IP.
Returns 429 status with ``Retry-After`` header when exceeded.

Uses lazy initialisation for the ``gql.Client`` — the schema is only fetched
from AniList's server on the first ``execute_async()`` call, avoiding a
1-2 second delay on every instantiation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from gql import Client, gql

from src.app.core.rate_limiter import RateLimiter
from src.app.core.retry_handler import retry_on_rate_limit

logger = logging.getLogger(__name__)


class AniListClient:
    """AniList GraphQL client with rate limiting and 429 retry.

    - Pre-request rate limiter: 80 req/min (safe margin below AniList's 90/min)
    - Post-429 retry: exponential backoff with ``Retry-After`` header support
    - Max 5 retries with jitter

    Usage::

        client = AniListClient()
        result = await client.get_media_by_id(1)
    """

    def __init__(self) -> None:
        self.rate_limiter = RateLimiter(max_requests=80, time_window=60.0)
        self._transport: AIOHTTPTransport | None = None
        self._client: Client | None = None

    # ------------------------------------------------------------------
    # Lazy-init properties
    # ------------------------------------------------------------------

    @property
    def transport(self) -> AIOHTTPTransport:
        if self._transport is None:
            from gql.transport.aiohttp import AIOHTTPTransport

            self._transport = AIOHTTPTransport(
                url="https://graphql.anilist.co/",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                ssl=True,
            )
        return self._transport

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client(
                transport=self.transport,
                fetch_schema_from_transport=True,
            )
        return self._client

    # ------------------------------------------------------------------
    # 429 detection for gql exceptions
    # ------------------------------------------------------------------

    @staticmethod
    def _is_anilist_429(exc: Exception) -> tuple[bool, float | None]:
        """Check if *exc* is an AniList 429 (Too Many Requests) response.

        AniList returns ``{"message": "Too Many Requests.", "status": 429}``
        as the GraphQL error payload.
        """
        exc_str = str(exc)
        if "429" in exc_str or "Too Many Requests" in exc_str:
            # Try to extract Retry-After from the error text
            import re

            match = re.search(r"retry.after[:\s]+(\d+)", exc_str, re.IGNORECASE)
            retry_after = float(match.group(1)) if match else None
            return True, retry_after
        return False, None

    # ------------------------------------------------------------------
    # Internal request helper with retry
    # ------------------------------------------------------------------

    async def _make_request(
        self, query_str: str, variables: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Make a rate-limited GraphQL request with 429 retry."""
        await self.rate_limiter.acquire()

        return await retry_on_rate_limit(
            lambda: self.client.execute_async(
                gql(query_str),
                variable_values=variables,
            ),
            is_rate_limited_fn=self._is_anilist_429,
            max_retries=5,
            base_delay=5.0,
            max_delay=120.0,
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def get_media_by_id(
        self, media_id: int, media_type: str = "ANIME"
    ) -> Optional[Dict[str, Any]]:
        """Get a single media entry by its AniList ID."""
        query_str = """
        query ($id: Int, $type: MediaType) {
          Media(id: $id, type: $type) {
            id
            title { romaji english native }
            format status
            description
            episodes chapters volumes duration
            averageScore popularity trending
            season seasonYear
            startDate { year month day }
            endDate { year month day }
            coverImage { large medium }
            bannerImage
            isAdult countryOfOrigin
            genres
            studios(isMain: true) { nodes { id name } }
            tags { name rank isMediaSpoiler isAdult }
            relations { edges {
              relationType(version: 2)
              node { id title { romaji english native } }
            } }
            nextAiringEpisode { episode airingAt }
          }
        }
        """
        variables: Dict[str, Any] = {"id": media_id, "type": media_type.upper()}
        try:
            result = await self._make_request(query_str, variables)
            return result.get("Media")
        except Exception:
            return None

    async def get_trending_media(
        self, media_type: str = "ANIME", limit: int = 20, page: int = 1
    ) -> List[Dict[str, Any]]:
        """Get trending media from AniList."""
        query_str = """
        query ($type: MediaType, $sort: [MediaSort], $page: Int, $per_page: Int) {
          Page(page: $page, perPage: $per_page) {
            media(type: $type, sort: $sort) {
              id
              title { romaji english native }
              format status
              episodes chapters volumes
              averageScore popularity trending
              season seasonYear
              startDate { year month day }
              coverImage { large medium }
              isAdult countryOfOrigin
            }
          }
        }
        """
        variables: Dict[str, Any] = {
            "type": media_type.upper(),
            "sort": ["TRENDING"],
            "page": page,
            "per_page": limit,
        }
        result = await self._make_request(query_str, variables)
        return result.get("Page", {}).get("media", [])

    async def search_media(
        self, query: str, media_type: str = "ANIME", limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search media by title query."""
        query_str = """
        query ($search: String, $type: MediaType, $page: Int, $per_page: Int) {
          Page(page: $page, perPage: $per_page) {
            media(search: $search, type: $type) {
              id
              title { romaji english native }
              format status
              episodes chapters volumes
              averageScore popularity trending
              season seasonYear
              startDate { year month day }
              coverImage { large medium }
              isAdult
            }
          }
        }
        """
        variables: Dict[str, Any] = {
            "search": query,
            "type": media_type.upper(),
            "page": 1,
            "per_page": limit,
        }
        result = await self._make_request(query_str, variables)
        return result.get("Page", {}).get("media", [])
