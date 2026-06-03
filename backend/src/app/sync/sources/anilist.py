"""AniListSeedAdapter — Stage 2 backfill pipeline.

Fetches full metadata (titles, synopsis, covers, genres, studios, tags,
relations, scores) from AniList's batch GraphQL API for all entries that
have ``anilist_id`` set but ``metadata_synced_at IS NULL``.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlmodel import select

from src.app.database import AsyncSessionLocal
from src.app.external.anilist_client import AniListClient
from src.app.models.enums import (
    MediaFormat,
    MediaStatus,
    MediaType,
    RelationType,
    Season,
)
from src.app.models.genre import Genre
from src.app.models.media_entry import MediaEntry
from src.app.models.media_external_ids import MediaExternalIds
from src.app.models.media_genre import MediaGenre
from src.app.models.media_studio import MediaStudio
from src.app.models.media_tag import MediaTag
from src.app.models.related_media import RelatedMedia
from src.app.models.studio import Studio
from src.app.models.tag import Tag
from src.app.sync.types import SeedExecutionContext, SeedRunResult

# ---------------------------------------------------------------------------
# AniList Batch GraphQL query — fetches up to 50 entries at once
# ---------------------------------------------------------------------------

BATCH_QUERY = """
query BatchMedia($ids: [Int], $page: Int) {
  Page(page: $page, perPage: 50) {
    media(id_in: $ids) {
      id
      title { romaji english native }
      type format status
      description(asHtml: false)
      coverImage { large medium }
      bannerImage
      episodes chapters volumes
      duration
      averageScore popularity trending
      startDate { year month day }
      endDate { year month day }
      season seasonYear
      countryOfOrigin isAdult
      genres
      tags { name rank isMediaSpoiler isAdult }
      studios(isMain: true) { nodes { id name } }
      relations { edges {
        relationType(version: 2)
        node { id }
      }}
      nextAiringEpisode { episode airingAt }
      airingSchedule(notYetAired: true, perPage: 25) {
        nodes { episode airingAt }
      }
    }
  }
}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_FORMAT_MAP: dict[str, MediaFormat] = {
    "TV": MediaFormat.TV,
    "TV_SHORT": MediaFormat.TV_SHORT,
    "MOVIE": MediaFormat.MOVIE,
    "SPECIAL": MediaFormat.SPECIAL,
    "OVA": MediaFormat.OVA,
    "ONA": MediaFormat.ONA,
    "MUSIC": MediaFormat.MUSIC,
    "MANGA": MediaFormat.MANGA,
    "NOVEL": MediaFormat.NOVEL,
    "ONE_SHOT": MediaFormat.ONE_SHOT,
}

_STATUS_MAP: dict[str, MediaStatus] = {
    "FINISHED": MediaStatus.finished,
    "RELEASING": MediaStatus.releasing,
    "NOT_YET_RELEASED": MediaStatus.not_yet_released,
    "CANCELLED": MediaStatus.cancelled,
    "HIATUS": MediaStatus.hiatus,
}

_RELATION_TYPE_MAP: dict[str, RelationType] = {
    "SEQUEL": RelationType.sequel,
    "PREQUEL": RelationType.prequel,
    "SIDE_STORY": RelationType.side_story,
    "PARENT": RelationType.parent,
    "SUMMARY": RelationType.summary,
    "ALTERNATIVE": RelationType.alternative,
    "SPIN_OFF": RelationType.spin_off,
    "ADAPTATION": RelationType.adaptation,
    "CHARACTER": RelationType.character,
    "OTHER": RelationType.other,
}


def _parse_anilist_date(
    d: dict[str, int | None] | None,
) -> date | None:
    """Parse an AniList date dict ``{year, month, day}`` into a ``date``."""
    if not d:
        return None
    year = d.get("year")
    month = d.get("month") or 1
    day = d.get("day") or 1
    if not year:
        return None
    try:
        return date(year=year, month=month, day=day)
    except (ValueError, TypeError):
        return None


def _slugify(name: str) -> str:
    """Simple slug generator for genre names."""
    return name.lower().replace(" ", "-").replace("/", "-")


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------


class AniListSeedAdapter:
    """Backfill adapter that fetches full metadata from AniList.

    Overrides the standard ``run()`` method to implement a custom loop
    that batches AniList IDs and fetches them in groups of 50 via the
    AniList batch GraphQL query.
    """

    def __init__(self, client: AniListClient | None = None) -> None:
        self.client = client or AniListClient()

    # ------------------------------------------------------------------
    # Main run loop
    # ------------------------------------------------------------------

    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        processed = 0
        failed = 0
        errors: list[dict[str, str]] = []

        if context.dry_run:
            return SeedRunResult(
                source="anilist",
                status="completed",
                processed_items=0,
                failed_items=0,
            )

        # Determine which entries need backfill
        async with AsyncSessionLocal() as session:
            query = select(MediaExternalIds).where(
                MediaExternalIds.anilist_id.is_not(None)
            )

            if context.only_unsynced:
                # Join with media_entries to only get entries whose
                # metadata_synced_at is NULL
                query = (
                    select(MediaExternalIds)
                    .join(MediaEntry, MediaExternalIds.media_id == MediaEntry.id)
                    .where(MediaEntry.metadata_synced_at.is_(None))
                )

            if context.limit:
                query = query.limit(context.limit)

            result = await session.execute(query)
            pending = result.scalars().all()

        total = len(pending)

        if total == 0:
            return SeedRunResult(
                source="anilist",
                status="completed",
                processed_items=0,
                failed_items=0,
            )

        # Process in batches of 50 (AniList batch limit)
        batch_size = min(context.batch_size or 50, 50)
        for i in range(0, total, batch_size):
            batch = pending[i : i + batch_size]
            anilist_ids = [ext.anilist_id for ext in batch if ext.anilist_id]

            if not anilist_ids:
                continue

            try:
                raw_results = await self.client._make_request(
                    BATCH_QUERY, {"ids": anilist_ids, "page": 1}
                )
                media_list = raw_results.get("Page", {}).get("media", [])
            except Exception as exc:
                failed += len(anilist_ids)
                errors.append(
                    {
                        "item": f"batch_{i}",
                        "source": "anilist",
                        "error": str(exc),
                    }
                )
                continue

            for media_data in media_list:
                try:
                    parsed = await self._parse_item(media_data)
                    await self._upsert_item(parsed)
                    processed += 1
                except Exception as exc:
                    failed += 1
                    errors.append(
                        {
                            "item": str(media_data.get("id")),
                            "source": "anilist",
                            "error": str(exc),
                        }
                    )

        status = "completed" if failed == 0 else "partial"
        return SeedRunResult(
            source="anilist",
            status=status,
            processed_items=processed,
            failed_items=failed,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Parse
    # ------------------------------------------------------------------

    async def _parse_item(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Normalise a single AniList API response dict."""
        return {
            "anilist_id": raw["id"],
            "title_romaji": raw.get("title", {}).get("romaji"),
            "title_english": raw.get("title", {}).get("english"),
            "title_native": raw.get("title", {}).get("native"),
            "media_type": raw.get("type", "").lower(),
            "format": _FORMAT_MAP.get(raw.get("format")),
            "status": _STATUS_MAP.get(raw.get("status", ""), MediaStatus.not_yet_released),
            "synopsis": raw.get("description"),
            "episode_count": raw.get("episodes"),
            "chapter_count": raw.get("chapters"),
            "volume_count": raw.get("volumes"),
            "duration_minutes": raw.get("duration"),
            "average_score": (
                float(raw["averageScore"] / 10.0) if raw.get("averageScore") else None
            ),
            "popularity": raw.get("popularity"),
            "trending": raw.get("trending"),
            "season": (
                raw.get("season", "").lower() if raw.get("season") else None
            ),
            "season_year": raw.get("seasonYear"),
            "start_date": _parse_anilist_date(raw.get("startDate")),
            "end_date": _parse_anilist_date(raw.get("endDate")),
            "cover_image_large": raw.get("coverImage", {}).get("large"),
            "cover_image_medium": raw.get("coverImage", {}).get("medium"),
            "banner_image": raw.get("bannerImage"),
            "is_adult": raw.get("isAdult", False),
            "country_of_origin": raw.get("countryOfOrigin"),
            "genres": raw.get("genres", []),
            "tags": raw.get("tags", []),
            "studios": raw.get("studios", {}).get("nodes", []),
            "relations": raw.get("relations", {}).get("edges", []),
        }

    # ------------------------------------------------------------------
    # Upsert
    # ------------------------------------------------------------------

    async def _upsert_item(self, parsed: dict[str, Any]) -> None:
        """Upsert a fully-parsed AniList entry into the database.

        This method creates its own DB session and handles:
        1. Finding or creating the ``media_entries`` row
        2. Upserting ``media_external_ids``
        3. Upserting genres / tags / studios / relations
        4. Setting ``metadata_synced_at = NOW()``
        """
        async with AsyncSessionLocal() as session:
            anilist_id = parsed["anilist_id"]

            # -- Find existing entry --
            result = await session.execute(
                select(MediaExternalIds).where(
                    MediaExternalIds.anilist_id == anilist_id
                )
            )
            existing_ext = result.scalar_one_or_none()

            if existing_ext:
                # Update existing media entry
                entry_result = await session.execute(
                    select(MediaEntry).where(MediaEntry.id == existing_ext.media_id)
                )
                entry = entry_result.scalar_one_or_none()
                if entry is None:
                    # Should not happen, but create a fallback
                    entry = MediaEntry(id=existing_ext.media_id, title_romaji="", media_type="anime")
                    session.add(entry)
                    await session.flush()
            else:
                # Create new entry + external IDs
                entry = MediaEntry(
                    id=uuid4(),
                    title_romaji=parsed.get("title_romaji") or "",
                    title_english=parsed.get("title_english"),
                    title_native=parsed.get("title_native"),
                    media_type=parsed.get("media_type", "anime"),
                    format=parsed.get("format"),
                    status=parsed.get("status", MediaStatus.not_yet_released),
                )
                session.add(entry)
                await session.flush()

                ext_ids = MediaExternalIds(
                    media_id=entry.id,
                    anilist_id=anilist_id,
                )
                session.add(ext_ids)
                await session.flush()
                existing_ext = ext_ids  # for downstream use

            # -- Update media entry fields --
            for field in (
                "title_english",
                "title_native",
                "synopsis",
                "episode_count",
                "chapter_count",
                "volume_count",
                "duration_minutes",
                "average_score",
                "popularity",
                "trending",
                "season_year",
                "cover_image_large",
                "cover_image_medium",
                "banner_image",
                "country_of_origin",
            ):
                val = parsed.get(field)
                if val is not None:
                    setattr(entry, field, val)

            # season (lowercase string -> Season enum)
            season_str = parsed.get("season")
            if season_str:
                try:
                    entry.season = Season(season_str)
                except ValueError:
                    pass

            # is_adult
            entry.is_adult = parsed.get("is_adult", False)

            # dates
            if parsed.get("start_date"):
                entry.start_date = datetime.combine(
                    parsed["start_date"], datetime.min.time()
                )
            if parsed.get("end_date"):
                entry.end_date = datetime.combine(
                    parsed["end_date"], datetime.min.time()
                )

            # format
            if parsed.get("format"):
                entry.format = parsed["format"]

            # status
            if parsed.get("status"):
                entry.status = parsed["status"]

            # Mark as synced
            entry.metadata_synced_at = datetime.utcnow()
            session.add(entry)
            await session.flush()

            # -- Upsert genres --
            for genre_name in parsed.get("genres", []):
                genre_result = await session.execute(
                    select(Genre).where(Genre.name == genre_name)
                )
                genre = genre_result.scalar_one_or_none()
                if not genre:
                    genre = Genre(
                        id=uuid4(),
                        name=genre_name,
                        slug=_slugify(genre_name),
                    )
                    session.add(genre)
                    await session.flush()

                # Link
                mg_result = await session.execute(
                    select(MediaGenre).where(
                        MediaGenre.media_id == entry.id,
                        MediaGenre.genre_id == genre.id,
                    )
                )
                if not mg_result.scalar_one_or_none():
                    session.add(MediaGenre(media_id=entry.id, genre_id=genre.id))

            # -- Upsert tags --
            for tag_data in parsed.get("tags", []):
                tag_name = tag_data.get("name", "")
                if not tag_name:
                    continue
                tag_result = await session.execute(
                    select(Tag).where(Tag.name == tag_name)
                )
                tag = tag_result.scalar_one_or_none()
                if not tag:
                    tag = Tag(
                        id=uuid4(),
                        name=tag_name,
                        is_adult=tag_data.get("isAdult", False),
                    )
                    session.add(tag)
                    await session.flush()

                # Link
                mt_result = await session.execute(
                    select(MediaTag).where(
                        MediaTag.media_id == entry.id,
                        MediaTag.tag_id == tag.id,
                    )
                )
                if not mt_result.scalar_one_or_none():
                    session.add(
                        MediaTag(
                            media_id=entry.id,
                            tag_id=tag.id,
                            rank=tag_data.get("rank", 0),
                        )
                    )

            # -- Upsert studios --
            for studio_data in parsed.get("studios", []):
                studio_name = studio_data.get("name", "")
                if not studio_name:
                    continue
                studio_result = await session.execute(
                    select(Studio).where(Studio.name == studio_name)
                )
                studio = studio_result.scalar_one_or_none()
                if not studio:
                    studio = Studio(
                        id=uuid4(),
                        name=studio_name,
                        anilist_id=studio_data.get("id"),
                    )
                    session.add(studio)
                    await session.flush()

                # Link
                ms_result = await session.execute(
                    select(MediaStudio).where(
                        MediaStudio.media_id == entry.id,
                        MediaStudio.studio_id == studio.id,
                    )
                )
                if not ms_result.scalar_one_or_none():
                    session.add(
                        MediaStudio(
                            media_id=entry.id,
                            studio_id=studio.id,
                            is_main=True,
                        )
                    )

            # -- Upsert relations --
            for edge in parsed.get("relations", []):
                rel_type_str = edge.get("relationType", "").upper()
                rel_type = _RELATION_TYPE_MAP.get(rel_type_str, RelationType.other)
                related_anilist_id = edge.get("node", {}).get("id")
                if not related_anilist_id:
                    continue

                # Look up the related media entry by anilist_id
                rel_ext_result = await session.execute(
                    select(MediaExternalIds).where(
                        MediaExternalIds.anilist_id == related_anilist_id
                    )
                )
                rel_ext = rel_ext_result.scalar_one_or_none()
                if not rel_ext:
                    continue  # Related media not yet seeded — skip

                # Check if relation already exists
                existing_rel_result = await session.execute(
                    select(RelatedMedia).where(
                        RelatedMedia.source_media_id == entry.id,
                        RelatedMedia.related_media_id == rel_ext.media_id,
                        RelatedMedia.relation_type == rel_type,
                    )
                )
                if not existing_rel_result.scalar_one_or_none():
                    session.add(
                        RelatedMedia(
                            id=uuid4(),
                            source_media_id=entry.id,
                            related_media_id=rel_ext.media_id,
                            relation_type=rel_type,
                        )
                    )

            await session.commit()
