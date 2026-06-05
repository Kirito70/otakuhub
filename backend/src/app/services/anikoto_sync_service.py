"""Anikoto provider matching and upsert service (ADR 078)."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.external.megaplay_client import MegaPlayEmbedResolver
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


class AnikotoSyncService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapping_repo = SourceMappingRepository(db)
        self.episode_repo = SourceEpisodeRepository(db)

    async def upsert_series(self, detail: dict[str, Any], *, dry_run: bool = False) -> tuple[UUID | None, int]:
        source_media_id = str(_pick(detail, "id", "series_id", "anime_id", "slug") or "").strip()
        if not source_media_id:
            raise ValueError("Anikoto series detail missing id")

        title = _pick(detail, "title", "name", "english_title", "romaji_title")
        normalized = normalize_title(str(title) if title else None)
        media_id, status, confidence = await self._match_media(detail, normalized)
        episodes = _extract_episodes(detail)
        payload = SourceMappingUpsert(
            media_id=media_id,
            source="anikoto",
            source_media_id=source_media_id,
            source_slug=str(_pick(detail, "slug") or source_media_id),
            source_url=_safe_url(_pick(detail, "url", "source_url")),
            source_title=str(title) if title else None,
            source_title_normalized=normalized,
            source_payload_hash=_hash_payload(detail),
            mapping_status=status,
            match_confidence=confidence,
            is_streaming_enabled=False,
            has_sub=any(_episode_language(e) == "sub" for e in episodes),
            has_dub=any(_episode_language(e) == "dub" for e in episodes),
            episode_count=len(episodes) or _int_or_none(_pick(detail, "episode_count", "episodes_count")),
            details_synced_at=datetime.now(UTC),
        )
        if dry_run:
            return media_id, len(episodes)

        mapping = await self.mapping_repo.upsert(payload)
        processed_episodes = 0
        for episode in episodes:
            source_episode_id = str(_pick(episode, "episode_embed_id", "embed_id", "id", "episode_id") or "").strip()
            if not source_episode_id:
                continue
            language = _episode_language(episode)
            await self.episode_repo.upsert(
                SourceEpisodeUpsert(
                    mapping_id=mapping.id,
                    media_id=media_id,
                    source="anikoto",
                    source_episode_id=source_episode_id,
                    episode_number=Decimal(str(_pick(episode, "episode_number", "number", "episode") or 0)),
                    title=str(_pick(episode, "title", "name") or "") or None,
                    language=language,
                    embed_path=_safe_embed_path(_pick(episode, "embed_path", "embed_url", "url"))
                    or MegaPlayEmbedResolver.build_episode_path(source_episode_id, language),
                    is_available=True,
                )
            )
            processed_episodes += 1
        return mapping.media_id, processed_episodes

    async def _match_media(self, detail: dict[str, Any], normalized_title: str | None) -> tuple[UUID | None, str, Decimal]:
        anilist_id = _int_or_none(_pick(detail, "anilist_id", "anilistId", "aniListId"))
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


def _safe_embed_path(value: Any) -> str | None:
    return MegaPlayEmbedResolver.safe_embed_path(value)


def _safe_url(value: Any) -> str | None:
    text = str(value) if value else None
    return text[:2048] if text else None


def _hash_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
