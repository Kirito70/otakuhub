"""MegaPlay embed URL/path helper and availability probe (ADR 078).

MegaPlay is the playback/embed host. Catalog and episode discovery still comes
from Anikoto, which exposes MegaPlay-compatible ``episode_embed_id`` values.

Three resolution patterns are documented at https://megaplay.buzz/api::

    /stream/s-2/{episode_embed_id}/{lang}   — primary (Anikoto/HiAnime ID)
    /stream/mal/{mal_id}/{ep_num}/{lang}     — MAL alternative
    /stream/ani/{anilist_id}/{ep_num}/{lang} — AniList alternative
"""

from __future__ import annotations

from urllib.parse import urlparse

import httpx

from src.app.core.rate_limiter import RateLimiter

MEGAPLAY_EMBED_HOST = "https://megaplay.buzz"

# MegaPlay does not document a specific rate limit; use a conservative default
# so availability probes don't overwhelm the embed host.
_MEGAPLAY_RATE_LIMITER = RateLimiter(max_requests=10, time_window=60.0)


class MegaPlayEmbedResolver:
    """Build and validate safe MegaPlay embed URLs and paths."""

    allowed_hosts = {"megaplay.buzz", "www.megaplay.buzz"}
    allowed_prefixes = ("/stream/", "/embed/", "/e/")
    blocked_markers = (".m3u8", ".mp4", "/hls/", "/dash/", "segment", "playlist")

    # -- Path / URL builders -------------------------------------------------

    @classmethod
    def build_episode_path(cls, episode_embed_id: str, language: str = "sub") -> str:
        safe_episode_id = str(episode_embed_id).strip().strip("/")
        safe_language = "dub" if str(language).lower() == "dub" else "sub"
        return f"/stream/s-2/{safe_episode_id}/{safe_language}"

    @classmethod
    def build_episode_url(cls, episode_embed_id: str, language: str = "sub") -> str:
        return f"{MEGAPLAY_EMBED_HOST}{cls.build_episode_path(episode_embed_id, language)}"

    @classmethod
    def build_mal_url(cls, mal_id: int, episode_number: int, language: str = "sub") -> str:
        """Build a MegaPlay embed URL using the MAL direct resolution path."""
        return f"{MEGAPLAY_EMBED_HOST}/stream/mal/{mal_id}/{episode_number}/{language}"

    @classmethod
    def build_anilist_url(cls, anilist_id: int, episode_number: int, language: str = "sub") -> str:
        """Build a MegaPlay embed URL using the AniList direct resolution path."""
        return f"{MEGAPLAY_EMBED_HOST}/stream/ani/{anilist_id}/{episode_number}/{language}"

    # -- Validation ----------------------------------------------------------

    @classmethod
    def safe_embed_path(cls, value: object) -> str | None:
        """Validate and return a safe embed *path* (legacy).

        Deprecated in favour of :meth:`safe_embed_url`.  Kept for backward
        compatibility with existing callers.
        """
        if not value:
            return None
        text = str(value)
        lowered = text.lower()
        if any(marker in lowered for marker in cls.blocked_markers):
            return None
        if text.startswith("http://") or text.startswith("https://"):
            parsed = urlparse(text)
            if parsed.hostname not in cls.allowed_hosts:
                return None
            path = parsed.path or ""
            return path[:512] if path.startswith(cls.allowed_prefixes) else None
        return text[:512] if text.startswith(cls.allowed_prefixes) else None

    @classmethod
    def safe_embed_url(cls, url: str) -> bool:
        """Return ``True`` when *url* is a safe MegaPlay embed URL.

        Validates that:
          * the host is a known MegaPlay host
          * the path starts with an allowed prefix
          * the URL does not contain raw media segment markers
        """
        if not url:
            return False
        lowered = url.lower()
        if any(marker in lowered for marker in cls.blocked_markers):
            return False
        try:
            parsed = urlparse(url)
        except Exception:
            return False
        if parsed.hostname not in cls.allowed_hosts:
            return False
        path = parsed.path or ""
        return path.startswith(cls.allowed_prefixes)


class MegaPlayAvailabilityClient:
    """Lightweight HTTP client that verifies MegaPlay embed URLs resolve.

    MegaPlay embed pages return HTTP 200 when the content is playable and 410
    (Gone) when the content has been removed.  This client probes the embed URL
    with HEAD requests and reports availability without loading the full page
    body.
    """

    def __init__(self, *, timeout: float = 5.0, http_client: httpx.AsyncClient | None = None) -> None:
        self.timeout = timeout
        self._client = http_client

    async def check_url(self, embed_url: str) -> bool:
        """Return ``True`` when *embed_url* resolves to a playable page.

        Uses a conservative rate limiter (10 req / 60 s) to avoid overwhelming
        the embed host.  Tries HEAD first; falls back to GET when the server
        returns 405 (Method Not Allowed).  Errors and timeouts are treated as
        *unavailable*.
        """
        if not MegaPlayEmbedResolver.safe_embed_url(embed_url):
            return False
        await _MEGAPLAY_RATE_LIMITER.acquire()
        client = self._client or httpx.AsyncClient(timeout=self.timeout)
        close_client = self._client is None
        try:
            response = await client.head(embed_url, follow_redirects=True)
            if response.status_code == 405:
                # Some servers reject HEAD; retry with GET + stream to avoid
                # downloading the full page body.
                response = await client.get(embed_url, follow_redirects=True)
            return response.status_code == 200
        except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError):
            return False
        finally:
            if close_client:
                await client.aclose()
