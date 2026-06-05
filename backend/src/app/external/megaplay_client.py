"""MegaPlay embed URL/path helper (ADR 078).

MegaPlay is the playback/embed host. Catalog and episode discovery still comes
from Anikoto, which exposes MegaPlay-compatible `episode_embed_id` values.
This helper builds approved embed paths only; it never fetches or exposes raw
media segment URLs.
"""

from __future__ import annotations

from urllib.parse import urlparse


MEGAPLAY_EMBED_HOST = "https://megaplay.buzz"


class MegaPlayEmbedResolver:
    """Build and validate safe MegaPlay embed paths."""

    allowed_hosts = {"megaplay.buzz", "www.megaplay.buzz"}
    allowed_prefixes = ("/stream/", "/embed/", "/e/")
    blocked_markers = (".m3u8", ".mp4", "/hls/", "/dash/", "segment", "playlist")

    @classmethod
    def build_episode_path(cls, episode_embed_id: str, language: str = "sub") -> str:
        safe_episode_id = str(episode_embed_id).strip().strip("/")
        safe_language = "dub" if str(language).lower() == "dub" else "sub"
        return f"/stream/s-2/{safe_episode_id}/{safe_language}"

    @classmethod
    def build_episode_url(cls, episode_embed_id: str, language: str = "sub") -> str:
        return f"{MEGAPLAY_EMBED_HOST}{cls.build_episode_path(episode_embed_id, language)}"

    @classmethod
    def safe_embed_path(cls, value: object) -> str | None:
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
