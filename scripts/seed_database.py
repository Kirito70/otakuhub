"""Deprecated compatibility shim for legacy root seed script.

Canonical seed entrypoints now live under backend CLI:
  - `otakuhub seed anime-offline`
  - `otakuhub seed all`
"""

from __future__ import annotations

import asyncio

from src.app.sync.entrypoints import run_seed_source


DEPRECATION_MESSAGE = (
    "DEPRECATED: `scripts/seed_database.py` is deprecated. "
    "Use `otakuhub seed anime-offline` (or `otakuhub seed all`) instead."
)


def main() -> int:
    print(DEPRECATION_MESSAGE)
    result = asyncio.run(run_seed_source(source="anime-offline", batch_size=50, dry_run=False))
    print(
        f"source={result['source']} job_id={result['job_id']} status={result['status']} "
        f"processed_items={result['processed_items']} failed_items={result['failed_items']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
