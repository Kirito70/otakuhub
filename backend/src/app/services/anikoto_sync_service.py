"""Anikoto provider matching and upsert service (ADR 078).

Stores full provider payloads, structured multilingual titles, and streaming
option URLs for each mapped series and episode.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.external.megaplay_client import MegaPlayEmbedResolver
from src.app.models.enums import MediaFormat, MediaStatus, MediaType
from src.app.models.media_entry import MediaEntry
from src.app.models.media_external_ids import MediaExternalIds
from src.app.repositories.source_provider_repository import SourceEpisodeRepository, SourceMappingRepository
from src.app.schemas.source_provider import SourceEpisodeUpsert, SourceMappingUpsert


def normalize_title(title: str | None) -> str | None:
    if not title:
        return None
    value = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value) or None


def _extract_source_titles(detail: dict[str, Any]) -> dict[str, Any]:
    """Extract structured multilingual titles from an Anikoto detail payload.

    Returns a dict with keys like ``romaji``, ``alternative``, ``native``,
    ``english`` and a catch-all ``all`` list.
    """
    titles: dict[str, Any] = {}
    romaji = str(_pick(detail, "title", "romaji_title", "english_title") or "")
    titles["romaji"] = romaji or None
    titles["alternative"] = str(_pick(detail, "alternative") or "") or None
    titles["native"] = str(_pick(detail, "native", "jp_title") or "") or None
    titles["english"] = str(_pick(detail, "english_title") or "") or None
    # The Anikoto ``titles`` field is a comma-separated list of all known
    # title variants for this series.
    raw_titles = str(_pick(detail, "titles") or "")
    titles["all"] = [t.strip() for t in raw_titles.split(",") if t.strip()] if raw_titles else []
    return titles


def _resolve_embed_url(
    episode: dict[str, Any],
    source_episode_id: str,
    language: str,
) -> str | None:
    """Extract the MegaPlay embed URL for *language* from the episode payload.

    The Anikoto API returns ``embed_url`` either as::

        # dict mapping language → URL (most common)
        {"sub": "https://megaplay.buzz/stream/s-2/130606/sub"}

        # plain string URL
        "https://megaplay.buzz/e/frieren-1"

    When the language key is missing or the string URL can't be validated,
    falls back to ``MegaPlayEmbedResolver.build_episode_url``.
    """
    embed_raw = episode.get("embed_url")
    if isinstance(embed_raw, dict):
        url = embed_raw.get(language)
        if url and isinstance(url, str) and MegaPlayEmbedResolver.safe_embed_url(url):
            return url
    elif isinstance(embed_raw, str) and MegaPlayEmbedResolver.safe_embed_url(embed_raw):
        return embed_raw
    # Fallback: reconstruct from episode_embed_id
    return MegaPlayEmbedResolver.build_episode_url(source_episode_id, language)


def _extract_embed_urls(episode: dict[str, Any]) -> dict[str, str] | None:
    """Extract the complete language→URL mapping from an episode payload."""
    embed_raw = episode.get("embed_url")
    if isinstance(embed_raw, dict):
        result: dict[str, str] = {}
        for lang, url in embed_raw.items():
            if isinstance(url, str) and MegaPlayEmbedResolver.safe_embed_url(url):
                result[lang] = url
        return result or None
    return None


class AnikotoSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapping_repo = SourceMappingRepository(db)
        self.episode_repo = SourceEpisodeRepository(db)

    async def upsert_series(self, detail: dict[str, Any], *, dry_run: bool = False, commit_mapping: bool = True) -> tuple[UUID | None, int]:
        source_media_id = str(_pick(detail, "id", "series_id", "anime_id", "slug") or "").strip()
        if not source_media_id:
            raise ValueError("Anikoto series detail missing id")

        title = _pick(detail, "title", "name", "english_title", "romaji_title")
        normalized = normalize_title(str(title) if title else None)
        media_id, status, confidence = await self._match_media(detail, normalized)
        episodes = _extract_episodes(detail)
        now = datetime.utcnow()

        payload = SourceMappingUpsert(
            media_id=media_id,
            source="anikoto",
            source_media_id=source_media_id,
            source_slug=str(_pick(detail, "slug") or source_media_id),
            source_url=_safe_url(_pick(detail, "url", "source_url")),
            source_title=str(title) if title else None,
            source_title_normalized=normalized,
            source_payload_hash=_hash_payload(detail),
            source_payload=detail,
            source_titles=_extract_source_titles(detail),
            mapping_status=status,
            match_confidence=confidence,
            is_streaming_enabled=False,
            has_sub=any(_episode_language(e) == "sub" for e in episodes),
            has_dub=any(_episode_language(e) == "dub" for e in episodes),
            episode_count=len(episodes) or _int_or_none(_pick(detail, "episode_count", "episodes_count", "episodes")),
            details_synced_at=now,
        )
        if dry_run:
            return media_id, len(episodes)

        mapping = await self.mapping_repo.upsert(payload, commit=commit_mapping)
        episode_upserts: list[SourceEpisodeUpsert] = []
        for episode in episodes:
            source_episode_id = str(_pick(episode, "episode_embed_id", "embed_id", "id", "episode_id") or "").strip()
            if not source_episode_id:
                continue
            language = _episode_language(episode)
            embed_url = _resolve_embed_url(episode, source_episode_id, language)
            episode_upserts.append(
                SourceEpisodeUpsert(
                    mapping_id=mapping.id,
                    media_id=media_id,
                    source="anikoto",
                    source_episode_id=source_episode_id,
                    episode_number=Decimal(str(_pick(episode, "episode_number", "number", "episode") or 0)),
                    title=str(_pick(episode, "title", "name") or "") or None,
                    language=language,
                    embed_url=embed_url,
                    embed_urls=_extract_embed_urls(episode),
                    source_payload=episode,
                    details_synced_at=now,
                    is_available=True,
                )
            )

        if episode_upserts:
            await self.episode_repo.bulk_upsert_episodes(
                mapping_id=mapping.id,
                media_id=media_id,
                episodes_data=episode_upserts,
                source="anikoto",
                now=now,
            )

        return mapping.media_id, len(episode_upserts)

    async def _match_media(self, detail: dict[str, Any], normalized_title: str | None) -> tuple[UUID | None, str, Decimal]:
        anilist_id = _int_or_none(_pick(detail, "anilist_id", "anilistId", "aniListId", "ani_id"))
        if anilist_id is not None:
            media_id = await self._media_id_by_external(anilist_id=anilist_id)
            if media_id:
                return media_id, "matched", Decimal("100.00")

        mal_id = _int_or_none(_pick(detail, "mal_id", "malId", "myanimelist_id"))
        if mal_id is not None:
            media_id = await self._media_id_by_external(mal_id=mal_id)
            if media_id:
                return media_id, "matched", Decimal("98.00")

        year = _int_or_none(_pick(detail, "year", "season_year", "release_year"))
        if normalized_title:
            media_id = await self._media_id_by_title(normalized_title=normalized_title, year=year)
            if media_id:
                return media_id, "matched", Decimal("92.00")

        # If this provider row carries stable cross-reference IDs, seed a
        # minimal canonical media entry. This is the first-entry path for new
        # titles before AniList/anime-offline backfill enriches metadata.
        if anilist_id is not None or mal_id is not None:
            media = await self._create_minimal_media_entry(detail, anilist_id=anilist_id, mal_id=mal_id)
            return media.id, "matched", Decimal("85.00")

        return None, "unmatched", Decimal("0.00")

    async def _media_id_by_external(self, *, anilist_id: int | None = None, mal_id: int | None = None) -> UUID | None:
        # `media_external_ids` is a canonical 1:1 cross-reference table and does
        # not have a soft-delete column in the baseline migration.
        stmt = select(MediaExternalIds)
        if anilist_id is not None:
            stmt = stmt.where(MediaExternalIds.anilist_id == anilist_id)
        if mal_id is not None:
            stmt = stmt.where(MediaExternalIds.mal_id == mal_id)
        result = await self.db.exec(stmt)
        row = result.one_or_none()
        return row.media_id if row else None

    async def _media_id_by_title(self, *, normalized_title: str, year: int | None) -> UUID | None:
        stmt = select(MediaEntry).where(MediaEntry.deleted_at.is_(None)).where(MediaEntry.media_type == "anime")
        if year is not None:
            stmt = stmt.where(MediaEntry.season_year == year)
        result = await self.db.exec(stmt)
        matches = [m for m in result.all() if normalized_title in {normalize_title(m.title_romaji), normalize_title(m.title_english), normalize_title(m.title_native)}]
        return matches[0].id if len(matches) == 1 else None

    async def _create_minimal_media_entry(self, detail: dict[str, Any], *, anilist_id: int | None, mal_id: int | None) -> MediaEntry:
        title = str(_pick(detail, "title", "name", "english_title", "romaji_title") or "Unknown provider title")
        entry = MediaEntry(
            title_romaji=title,
            title_english=str(_pick(detail, "english_title", "alternative") or "") or None,
            title_native=str(_pick(detail, "native", "jp_title") or "") or None,
            media_type=MediaType.anime,
            format=_map_anikoto_format(detail),
            status=_map_anikoto_status(_pick(detail, "status")),
            synopsis=str(_pick(detail, "description", "synopsis") or "") or None,
            cover_image_large=str(_pick(detail, "poster", "cover", "image") or "") or None,
            cover_image_medium=str(_pick(detail, "poster", "cover", "image") or "") or None,
            episode_count=_int_or_none(_pick(detail, "episode_count", "episodes_count", "episodes")),
            average_score=_score_or_none(_pick(detail, "score", "rating_score")),
            season_year=_int_or_none(_pick(detail, "year", "season_year", "release_year")),
            metadata_synced_at=None,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)

        external_ids = MediaExternalIds(media_id=entry.id, anilist_id=anilist_id, mal_id=mal_id)
        self.db.add(external_ids)
        await self.db.commit()
        return entry


def _pick(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _score_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _map_anikoto_status(value: Any) -> MediaStatus:
    text = str(value or "").lower()
    if "finished" in text:
        return MediaStatus.finished
    if "airing" in text or "releasing" in text:
        return MediaStatus.releasing
    if "not" in text and "released" in text:
        return MediaStatus.not_yet_released
    return MediaStatus.not_yet_released


def _map_anikoto_format(detail: dict[str, Any]) -> MediaFormat | None:
    terms = detail.get("terms_by_type")
    type_terms = []
    if isinstance(terms, dict) and isinstance(terms.get("type"), list):
        type_terms = [str(item).lower() for item in terms["type"]]
    text = " ".join(type_terms + [str(_pick(detail, "type", "format") or "").lower()])
    if "movie" in text:
        return MediaFormat.MOVIE
    if "ova" in text:
        return MediaFormat.OVA
    if "ona" in text:
        return MediaFormat.ONA
    if "special" in text:
        return MediaFormat.SPECIAL
    if "music" in text:
        return MediaFormat.MUSIC
    return MediaFormat.TV


def _extract_episodes(detail: dict[str, Any]) -> list[dict[str, Any]]:
    raw = detail.get("episodes") or detail.get("episode_list") or []
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def _episode_language(episode: dict[str, Any]) -> str:
    raw = str(_pick(episode, "language", "lang", "type") or "sub").lower()
    if "dub" in raw:
        return "dub"
    if "raw" in raw:
        return "raw"
    return "sub" if "sub" in raw or raw == "" else "unknown"


def _safe_url(value: Any) -> str | None:
    text = str(value) if value else None
    return text[:2048] if text else None


def _hash_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
