"""Service for provider/source data — playback API support (Phase 25)."""

from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.repositories.media_repository import MediaRepository
from src.app.repositories.source_provider_repository import (
    SourceEpisodeRepository,
    SourceMappingRepository,
)
from src.app.schemas.source_provider import (
    ConsolidatedEpisodeSourceItem,
    ConsolidatedEpisodeSourceResponse,
    ConsolidatedSourceInfo,
    MediaSourceResponse,
    SourceEpisodeItem,
    SourceMappingDetail,
)


class SourceProviderService:
    """Service for user-facing provider source data queries."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._mapping_repo = SourceMappingRepository(db_session)
        self._episode_repo = SourceEpisodeRepository(db_session)
        self._media_repo = MediaRepository(db_session)

    async def get_sources_for_media(self, media_id: UUID) -> MediaSourceResponse:
        """Get all source mappings with episodes for a media entry."""
        mappings = await self._mapping_repo.get_mappings_by_media(media_id=media_id)

        items: list[SourceMappingDetail] = []
        for mapping in mappings:
            episodes = await self._episode_repo.list_for_mapping(mapping_id=mapping.id)

            episode_list = [
                SourceEpisodeItem(
                    id=ep.id,
                    episode_number=float(ep.episode_number),
                    title=ep.title,
                    language=ep.language,
                    embed_url=ep.embed_url,
                    is_available=ep.is_available,
                )
                for ep in episodes
            ]

            items.append(
                SourceMappingDetail(
                    id=mapping.id,
                    source=mapping.source,
                    source_title=mapping.source_title,
                    mapping_status=mapping.mapping_status,
                    match_confidence=mapping.match_confidence,
                    is_streaming_enabled=mapping.is_streaming_enabled,
                    has_sub=mapping.has_sub,
                    has_dub=mapping.has_dub,
                    episode_count=mapping.episode_count,
                    episode_list=episode_list,
                )
            )

        return MediaSourceResponse(items=items, total=len(items))

    async def get_consolidated_episodes(
        self,
        media_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> ConsolidatedEpisodeSourceResponse:
        """Get consolidated episodes — canonical episodes merged with source providers.

        For each canonical episode (paginated), attaches all available source
        provider options (language, embed URL, availability) from every provider
        that has matching episode data.
        """
        # 1. Get canonical episodes (paginated)
        canon_items, total = await self._media_repo.get_episodes_by_media_id(
            media_id=media_id,
            limit=limit,
            offset=offset,
        )

        # 2. Get all available source episodes for this media
        source_episodes = await self._episode_repo.get_episodes_by_media(media_id=media_id)

        # 3. Build lookup: episode_number -> list of sources
        sources_by_number: dict[float, list[ConsolidatedSourceInfo]] = defaultdict(list)
        for se in source_episodes:
            ep_num = float(se.episode_number)
            sources_by_number[ep_num].append(
                ConsolidatedSourceInfo(
                    source=se.source,
                    language=se.language,
                    embed_url=se.embed_url,
                    is_available=se.is_available,
                )
            )

        # 4. Merge canonical episodes with their sources
        items = [
            ConsolidatedEpisodeSourceItem(
                episode_number=float(ep.episode_number),
                canonical_title=ep.title,
                canonical_air_date=ep.air_date,
                sources=sources_by_number.get(float(ep.episode_number), []),
            )
            for ep in canon_items
        ]

        return ConsolidatedEpisodeSourceResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
