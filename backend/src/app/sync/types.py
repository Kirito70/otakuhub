from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol


SeedStatus = Literal["completed", "partial", "failed"]


@dataclass(slots=True)
class SeedExecutionContext:
    source: str
    job_id: str
    dry_run: bool = False
    limit: int | None = None
    batch_size: int | None = None
    only_unsynced: bool = False
    user_id: str | None = None


@dataclass(slots=True)
class SeedRunResult:
    source: str
    status: SeedStatus
    processed_items: int
    failed_items: int
    errors: list[dict[str, str]] = field(default_factory=list)


class SeedSourceAdapter(Protocol):
    async def run(self, context: SeedExecutionContext) -> SeedRunResult:
        ...
