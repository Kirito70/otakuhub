from __future__ import annotations

from src.app.sync.ingestion import IngestionRetryPolicy, run_ingestion
from src.app.sync.types import SeedExecutionContext, SeedRunResult


class AniListSeedAdapter:
    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        item_count = context.limit or 0

        async def _parse_item(item_index: int) -> dict[str, int | bool]:
            return {"index": item_index, "only_unsynced": context.only_unsynced}

        async def _upsert_item(_: dict[str, int | bool]) -> None:
            return None

        return await run_ingestion(
            context=context,
            item_count=item_count,
            parse_item=_parse_item,
            upsert_item=_upsert_item,
            retry_policy=IngestionRetryPolicy(),
        )
