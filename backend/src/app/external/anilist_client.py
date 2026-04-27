"""AniList GraphQL client with rate limiting."""

from typing import Dict, Any, List, Optional
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql import gql

from src.app.core.rate_limiter import RateLimiter


class AniListClient:
    """AniList GraphQL client with rate limiting."""

    def __init__(self):
        # Initialize rate limiter - 100 requests per minute (AniList limit)
        self.rate_limiter = RateLimiter(max_requests=100, time_window=60)

        # Initialize GraphQL transport
        self.transport = AIOHTTPTransport(
            url="https://graphql.anilist.co/",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        # Initialize client
        self.client = Client(
            transport=self.transport,
            fetch_schema_from_transport=True,
            subscribe_transport=self.transport
        )

    async def _make_request(self, query_str: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to the AniList API with rate limiting."""
        # Wait for rate limit token
        await self.rate_limiter.acquire()

        try:
            result = await self.client.execute_async(
                gql(query_str),
                variable_values=variables
            )
            return result
        except Exception as e:
            print(f"AniList API error: {e}")
            raise

    async def get_media_by_id(self, media_id: int, media_type: str = "ANIME") -> Optional[Dict[str, Any]]:
        """Get media details by ID."""
        query_str = """
        query ($id: Int, $type: MediaType) {
          Media(id: $id, type: $type) {
            id
            title {
              romaji
              english
              native
            }
            format
            status
            description
            episodes
            chapters
            volumes
            duration
            averageScore
            popularity
            trending
            season
            seasonYear
            startDate {
              year
              month
              day
            }
            endDate {
              year
              month
              day
            }
            coverImage {
              large
              medium
            }
            bannerImage
            isAdult
            countryOfOrigin
            genres
            studios {
              nodes {
                name
              }
            }
            tags {
              name
              rank
            }
            relations {
              edges {
                relationType
                node {
                  id
                  title {
                    romaji
                    english
                    native
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            "id": media_id,
            "type": media_type.upper()
        }

        try:
            result = await self._make_request(query_str, variables)
            return result.get("Media")
        except Exception:
            return None

    async def get_trending_media(self, media_type: str = "ANIME",
                               limit: int = 20, page: int = 1) -> List[Dict[str, Any]]:
        """Get trending media."""
        query_str = """
        query ($type: MediaType, $sort: [MediaSort], $page: Int, $per_page: Int) {
          Page(page: $page, perPage: $per_page) {
            media(type: $type, sort: $sort) {
              id
              title {
                romaji
                english
                native
              }
              format
              status
              episodes
              chapters
              volumes
              averageScore
              popularity
              trending
              season
              seasonYear
              startDate {
                year
                month
                day
              }
              coverImage {
                large
                medium
              }
              isAdult
              countryOfOrigin
            }
          }
        }
        """

        variables = {
            "type": media_type.upper(),
            "sort": ["TRENDING"],
            "page": page,
            "per_page": limit
        }

        result = await self._make_request(query_str, variables)
        return result.get("Page", {}).get("media", [])

    async def search_media(self, query: str, media_type: str = "ANIME",
                          limit: int = 20) -> List[Dict[str, Any]]:
        """Search media by query."""
        query_str = """
        query ($search: String, $type: MediaType, $page: Int, $per_page: Int) {
          Page(page: $page, perPage: $per_page) {
            media(search: $search, type: $type) {
              id
              title {
                romaji
                english
                native
              }
              format
              status
              episodes
              chapters
              volumes
              averageScore
              popularity
              trending
              season
              seasonYear
              startDate {
                year
                month
                day
              }
              coverImage {
                large
                medium
              }
              isAdult
            }
          }
        }
        """

        variables = {
            "search": query,
            "type": media_type.upper(),
            "page": 1,
            "per_page": limit
        }

        result = await self._make_request(query_str, variables)
        return result.get("Page", {}).get("media", [])
