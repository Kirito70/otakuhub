from __future__ import annotations

from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.sync.job_runner import SyncJobRunner
from src.app.sync.orchestrator import SeedOrchestrator
from src.app.sync.sources.anilist import AniListSeedAdapter
from src.app.sync.sources.anime_offline import AnimeOfflineSeedAdapter
from src.app.sync.sources.jikan import JikanSeedAdapter
from src.app.sync.sources.mangadex import MangaDexSeedAdapter
from src.app.sync.sources.anikoto import AnikotoSourceAdapter


def build_seed_orchestrator(session: AsyncSession) -> SeedOrchestrator:
    return SeedOrchestrator(
        job_runner=SyncJobRunner(session),
        adapters={
            # Lazy factories keep source-specific setup isolated. In particular,
            # provider sync commands must not initialize/download anime-offline
            # data when they only need the Anikoto/MegaPlay adapter.
            "anime-offline": AnimeOfflineSeedAdapter,
            "anilist": AniListSeedAdapter,
            "mangadex": MangaDexSeedAdapter,
            "jikan": JikanSeedAdapter,
            "anikoto_full_catalog": lambda: AnikotoSourceAdapter(mode="full"),
            "anikoto_recent_refresh": lambda: AnikotoSourceAdapter(mode="recent"),
        },
    )
