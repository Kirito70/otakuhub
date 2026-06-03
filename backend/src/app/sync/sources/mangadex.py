"""MangaDexSeedAdapter — Stage 3 manga detail pipeline.

Fetches chapter data and cover art for manga-type entries (manga, manhwa,
manhua, light_novel, novel) using the MangaDex REST API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlmodel import select

from src.app.database import AsyncSessionLocal
from src.app.external.mangadex_client import MangaDexClient
from src.app.models.chapter import Chapter
from src.app.models.enums import MediaType
from src.app.models.media_entry import MediaEntry
from src.app.models.media_external_ids import MediaExternalIds
from src.app.sync.types import SeedExecutionContext, SeedRunResult

# Media types that MangaDex handles
_MANGA_TYPES = frozenset({
    MediaType.manga,
    MediaType.manhwa,
    MediaType.manhua,
    MediaType.light_novel,
    MediaType.novel,
})


def _parse_mangadex_chapter(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Parse a single MangaDex chapter resource into a simpler dict.

    Returns ``None`` if the chapter has no useful data.
    """
    attributes = raw.get("attributes", {}) or {}
    chapter_str = attributes.get("chapter")
    if not chapter_str:
        return None

    try:
        chapter_number = float(chapter_str)
    except (ValueError, TypeError):
        return None

    published_str = attributes.get("publishAt") or attributes.get("createdAt")
    published_at: datetime | None = None
    if published_str:
        try:
            # MangaDex uses ISO 8601 format
            published_at = datetime.fromisoformat(
                published_str.replace("Z", "+00:00")
            )
        except (ValueError, TypeError):
            pass

    return {
        "mangadex_chapter_id": raw.get("id"),
        "chapter_number": chapter_number,
        "volume_number": attributes.get("volume"),
        "title": attributes.get("title"),
        "published_at": published_at,
    }


class MangaDexSeedAdapter:
    """Seed adapter that fetches chapter data for manga-type entries.

    Overrides the standard ``run()`` method to implement a custom loop
    that queries the database for manga entries with ``mangadex_id`` set,
    then fetches their chapters via the MangaDex REST API.
    """

    def __init__(self, client: MangaDexClient | None = None) -> None:
        self.client = client or MangaDexClient()

    # ------------------------------------------------------------------
    # Main run loop
    # ------------------------------------------------------------------

    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        processed = 0
        failed = 0
        errors: list[dict[str, str]] = []

        if context.dry_run:
            return SeedRunResult(
                source="mangadex",
                status="completed",
                processed_items=0,
                failed_items=0,
            )

        # Find manga-type entries that have mangadex_id set
        async with AsyncSessionLocal() as session:
            query = (
                select(MediaExternalIds)
                .join(MediaEntry, MediaExternalIds.media_id == MediaEntry.id)
                .where(
                    MediaExternalIds.mangadex_id.is_not(None),
                    MediaEntry.media_type.in_(list(_MANGA_TYPES)),
                )
            )

            if context.only_unsynced:
                query = query.where(MediaEntry.metadata_synced_at.is_(None))

            if context.limit:
                query = query.limit(context.limit)

            result = await session.execute(query)
            pending = result.scalars().all()

        total = len(pending)

        if total == 0:
            return SeedRunResult(
                source="mangadex",
                status="completed",
                processed_items=0,
                failed_items=0,
            )

        for ext in pending:
            try:
                parsed = await self._parse_item(ext)
                if parsed is not None:
                    await self._upsert_item(parsed)
                processed += 1
            except Exception as exc:
                failed += 1
                errors.append(
                    {
                        "item": str(ext.mangadex_id or ext.media_id),
                        "source": "mangadex",
                        "error": str(exc),
                    }
                )

        status = "completed" if failed == 0 else "partial"
        return SeedRunResult(
            source="mangadex",
            status=status,
            processed_items=processed,
            failed_items=failed,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Parse — fetches chapters from MangaDex
    # ------------------------------------------------------------------

    async def _parse_item(
        self, ext: MediaExternalIds
    ) -> dict[str, Any] | None:
        """Fetch chapter data from MangaDex for a single entry.

        Returns a dict with ``mangadex_id``, ``media_id``, and ``chapters``.
        """
        mangadex_id = ext.mangadex_id
        if not mangadex_id:
            return None

        # Fetch chapters (up to 500 per page)
        raw_chapters = await self.client.get_chapters(
            mangadex_id, limit=500, offset=0
        )

        chapters = []
        for raw in raw_chapters:
            parsed = _parse_mangadex_chapter(raw)
            if parsed is not None:
                chapters.append(parsed)

        return {
            "mangadex_id": mangadex_id,
            "media_id": ext.media_id,
            "chapters": chapters,
        }

    # ------------------------------------------------------------------
    # Upsert — inserts chapters and sets metadata_synced_at
    # ------------------------------------------------------------------

    async def _upsert_item(self, parsed: dict[str, Any]) -> None:
        """Insert or update chapters for a manga entry.

        Also updates ``metadata_synced_at = NOW()`` on the media entry.
        """
        media_id = parsed["media_id"]
        chapters = parsed["chapters"]

        async with AsyncSessionLocal() as session:
            for ch in chapters:
                # Check if chapter already exists
                existing_result = await session.execute(
                    select(Chapter).where(
                        Chapter.media_id == media_id,
                        Chapter.chapter_number == ch["chapter_number"],
                    )
                )
                existing = existing_result.scalar_one_or_none()
                if existing:
                    # Update fields that may have changed
                    if ch.get("title"):
                        existing.title = ch["title"]
                    if ch.get("published_at"):
                        existing.published_at = ch["published_at"]
                    if ch.get("volume_number"):
                        existing.volume_number = ch["volume_number"]
                    if ch.get("mangadex_chapter_id"):
                        existing.mangadex_chapter_id = ch["mangadex_chapter_id"]
                    session.add(existing)
                else:
                    chapter = Chapter(
                        id=uuid4(),
                        media_id=media_id,
                        chapter_number=ch["chapter_number"],
                        volume_number=ch.get("volume_number"),
                        title=ch.get("title"),
                        published_at=ch.get("published_at"),
                        mangadex_chapter_id=ch.get("mangadex_chapter_id"),
                    )
                    session.add(chapter)

            # Update metadata_synced_at
            entry_result = await session.execute(
                select(MediaEntry).where(MediaEntry.id == media_id)
            )
            entry = entry_result.scalar_one_or_none()
            if entry:
                entry.metadata_synced_at = datetime.utcnow()
                session.add(entry)

            await session.commit()
