"""AniList GraphQL client with rate limiting.

Uses lazy initialisation for the ``gql.Client`` — the schema is only fetched
from AniList's server on the first ``execute_async()`` call, avoiding a
1-2 second delay on every instantiation.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql import gql

from src.app.core.rate_limiter import RateLimiter


class AniListClient:
    """AniList GraphQL client with rate limiting.

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
            self._transport = AIOHTTPTransport(
                url="https://graphql.anilist.co/",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._transport

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client(
                transport=self.transport,
                fetch_schema_from_transport=True,
                subscribe_transport=self.transport,
            )
        return self._client

    # ------------------------------------------------------------------
    # Internal request helper
    # ------------------------------------------------------------------

    async def _make_request(
        self, query_str: str, variables: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Make a rate-limited GraphQL request and return the raw dict."""
        await self.rate_limiter.acquire()

        try:
            result = await self.client.execute_async(
                gql(query_str),
                variable_values=variables,
            )
            return result
        except Exception as e:
            print(f"AniList API error: {e}")
            raise

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
