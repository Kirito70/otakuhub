"""Debug the seed failure using the exact same path."""
import asyncio
import sys

# Monkey-patch the ingestion loop to print first 3 errors
import src.app.sync.ingestion as ingestion_mod

_original_run = ingestion_mod.run_ingestion


async def debug_run(*args, **kwargs):
    result = await _original_run(*args, **kwargs)
    if result.errors:
        for i, err in enumerate(result.errors[:3]):
            print(f"  ERROR #{i}: {err}")
    return result


ingestion_mod.run_ingestion = debug_run

from src.app.sync.entrypoints import run_seed_source


async def main():
    result = await run_seed_source(
        source="anime-offline",
        batch_size=10,
        dry_run=False,
    )
    print(f"\nResult: status={result['status']} "
          f"processed={result['processed_items']} "
          f"failed={result['failed_items']}")


asyncio.run(main())
