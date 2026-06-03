"""AnimeOfflineSeedAdapter — Stage 1 seed pipeline.

Loads the ``anime-offline-database.json`` file (either from a local path
or by downloading it from GitHub) and upserts every anime entry into
``media_entries`` + ``media_external_ids``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlmodel import select

from src.app.database import AsyncSessionLocal
from src.app.models.media_entry import MediaEntry
from src.app.models.media_external_ids import MediaExternalIds
from src.app.models.enums import MediaFormat, MediaStatus, MediaType
from src.app.sync.ingestion import IngestionRetryPolicy, run_ingestion
from src.app.sync.types import SeedExecutionContext, SeedRunResult

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FORMAT_MAP: dict[str, MediaFormat] = {
    "TV": MediaFormat.TV,
    "Movie": MediaFormat.MOVIE,
    "OVA": MediaFormat.OVA,
    "ONA": MediaFormat.ONA,
    "Special": MediaFormat.SPECIAL,
}

_STATUS_MAP: dict[str, MediaStatus] = {
    "FINISHED": MediaStatus.finished,
    "RELEASING": MediaStatus.releasing,
    "NOT_YET_RELEASED": MediaStatus.not_yet_released,
    "CANCELLED": MediaStatus.cancelled,
    "HIATUS": MediaStatus.hiatus,
}


def _map_format(entry_type: str) -> MediaFormat | None:
    """Map anime-offline format strings to our MediaFormat enum."""
    # Normalise: "TV", "Movie", "OVA", "ONA", "Special"
    if not entry_type:
        return None
    return _FORMAT_MAP.get(entry_type, MediaFormat.TV)


def _map_status(entry_status: str) -> MediaStatus:
    """Map anime-offline status strings to our MediaStatus enum.

    Accepts both uppercase (``FINISHED``) and title-case (``Finished``)
    variants.
    """
    normalised = entry_status.upper().replace(" ", "_") if entry_status else ""
    return _STATUS_MAP.get(normalised, MediaStatus.not_yet_released)


def _find_id(entry: dict[str, Any], source_name: str) -> int | str | None:
    """Extract an external ID from the ``sources`` list.

    The ``sources`` field is a list of ``{"label": "...", "url": "..."}``
    dicts.  This helper looks for the label matching *source_name* and
    extracts the last path segment of the URL as the ID.
    """
    for source in entry.get("sources", []):
        if source.get("label", "").lower() == source_name.lower():
            url = source.get("url", "")
            if url:
                return url.rstrip("/").split("/")[-1]
    return None


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class AnimeOfflineSeedAdapter:
    """Seed adapter that loads data from ``anime-offline-database.json``.

    The JSON is loaded once in ``__init__`` (with automatic download fallback)
    and then each entry is parsed and upserted by the ingestion loop.
    """

    def __init__(self, data_path: str | None = None) -> None:
        self._data: list[dict[str, Any]] = []
        self._load_data(data_path)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_data(self, data_path: str | None = None) -> None:
        """Load the anime-offline-database JSON from a local file or GitHub.

        Resolution order:
        1. ``ANIME_OFFLINE_DATABASE_PATH`` environment variable
        2. *data_path* argument (for testing)
        3. ``backend/data/anime-offline-database.json``
        4. Download from GitHub (asynchronous via aiohttp/httpx)
        """
        candidate = (
            data_path
            or os.environ.get("ANIME_OFFLINE_DATABASE_PATH")
        )

        if candidate and Path(candidate).is_file():
            self._load_from_file(candidate)
            return

        # Fallback: check the default location
        default = Path(__file__).resolve().parent.parent.parent.parent / "data" / "anime-offline-database.json"
        # ../../../../data/anime-offline-database.json relative to this file
        # src/app/sync/sources/anime_offline.py -> up 4 levels to backend/
        resolved_default = default.resolve()
        if resolved_default.is_file():
            self._load_from_file(str(resolved_default))
            return

        # Last resort: download
        import asyncio
        import httpx

        url = (
            "https://raw.githubusercontent.com/manami-project/"
            "anime-offline-database/master/anime-offline-database.json"
        )
        print(f"Downloading anime-offline-database from {url} ...")
        response = httpx.get(url, follow_redirects=True, timeout=120.0)
        response.raise_for_status()
        raw = response.json()
        self._data = raw.get("data", [])
        print(f"Downloaded {len(self._data)} entries.")

    def _load_from_file(self, path: str) -> None:
        """Load JSON from a local file path."""
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self._data = raw.get("data", [])
        print(f"Loaded {len(self._data)} entries from {path}.")

    # ------------------------------------------------------------------
    # Adapter interface
    # ------------------------------------------------------------------

    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        item_count = context.limit if context.limit is not None else len(self._data)

        async def _parse_item(item_index: int) -> dict[str, Any]:
            return self._parse_item(item_index)

        async def _upsert_item(parsed: dict[str, Any]) -> None:
            await self._upsert_item(parsed)

        return await run_ingestion(
            context=context,
            item_count=item_count,
            parse_item=_parse_item,
            upsert_item=_upsert_item,
            retry_policy=IngestionRetryPolicy(),
        )

    # ------------------------------------------------------------------
    # Item parsing
    # ------------------------------------------------------------------

    def _parse_item(self, item_index: int) -> dict[str, Any]:
        """Parse a single anime-offline entry into our internal format."""
        entry = self._data[item_index]

        anilist_id_raw = _find_id(entry, "anilist")
        mal_id_raw = _find_id(entry, "myanimelist")
        anidb_id_raw = _find_id(entry, "anidb")
        kitsu_id_raw = _find_id(entry, "kitsu")

        return {
            "title_romaji": entry.get("title", ""),
            "title_english": next(
                (
                    s["title"]
                    for s in entry.get("sources", [])
                    if s.get("label") == "English"
                ),
                None,
            ),
            "title_native": next(
                (
                    s["title"]
                    for s in entry.get("sources", [])
                    if s.get("label") == "Native"
                ),
                None,
            ),
            "media_type": MediaType.anime,
            "format": _map_format(entry.get("type", "")),
            "status": _map_status(entry.get("status", "")),
            "synopsis": None,
            "episode_count": entry.get("episodes"),
            "cover_image": entry.get("picture"),
            "anilist_id": int(anilist_id_raw) if anilist_id_raw else None,
            "mal_id": int(mal_id_raw) if mal_id_raw else None,
            "anidb_id": int(anidb_id_raw) if anidb_id_raw else None,
            "kitsu_id": kitsu_id_raw,
        }

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------

    async def _upsert_item(self, parsed: dict[str, Any]) -> None:
        """Insert or update a media entry and its external IDs."""
        async with AsyncSessionLocal() as session:
            # Check if we already have this entry by anilist_id
            if parsed["anilist_id"]:
                result = await session.execute(
                    select(MediaExternalIds).where(
                        MediaExternalIds.anilist_id == parsed["anilist_id"]
                    )
                )
                existing = result.scalar_one_or_none()
                if existing:
                    return  # Already seeded — skip

            # Create new MediaEntry
            entry = MediaEntry(
                id=uuid4(),
                title_romaji=parsed["title_romaji"],
                title_english=parsed["title_english"],
                title_native=parsed["title_native"],
                media_type=parsed["media_type"],
                format=parsed["format"],
                status=parsed["status"],
                episode_count=parsed["episode_count"],
                cover_image_large=parsed["cover_image"],
                cover_image_medium=parsed["cover_image"],
            )
            session.add(entry)
            await session.flush()  # Get the UUID

            # Create MediaExternalIds — the anilist_id may not exist, but
            # if it does, it's our canonical cross-ref.
            ext_ids = MediaExternalIds(
                media_id=entry.id,
                anilist_id=parsed["anilist_id"],
                mal_id=parsed["mal_id"],
                anidb_id=parsed["anidb_id"],
                kitsu_id=str(parsed["kitsu_id"]) if parsed["kitsu_id"] else None,
            )
            session.add(ext_ids)
            await session.commit()
