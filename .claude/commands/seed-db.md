# Generate and Run the Database Seed Script

This command generates the full anime database seed pipeline.

## What This Does
1. Downloads the latest `anime-offline-database` release from GitHub
2. Parses the JSON and bulk-inserts into `media_entries` + `media_external_ids`
3. Marks all entries for AniList backfill (sets `metadata_synced_at = NULL`)
4. Reports counts and any errors

## Script to Generate: `scripts/seed_anime_db.py`

```python
#!/usr/bin/env python3
"""
OtakuHub — Anime Database Seed Script
Downloads anime-offline-database and bulk-inserts into PostgreSQL.
Run once at initial deployment, then use weekly sync for updates.
Usage: python scripts/seed_anime_db.py [--dry-run]
"""
import asyncio
import httpx
import json
import sys
from sqlalchemy.dialects.postgresql import insert as pg_insert

OFFLINE_DB_URL = "https://github.com/manami-project/anime-offline-database/releases/latest/download/anime-offline-database-minified.json"

async def download_database() -> list[dict]:
    print("Downloading anime-offline-database...")
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        response = await client.get(OFFLINE_DB_URL)
        response.raise_for_status()
    data = response.json()
    print(f"Downloaded {len(data['data'])} entries")
    return data["data"]

def extract_external_id(sources: list[str], domain: str) -> str | None:
    for url in sources:
        if domain in url:
            return url.rstrip("/").split("/")[-1]
    return None

async def seed(dry_run: bool = False) -> None:
    entries = await download_database()
    
    async with get_db_session() as db:
        media_rows = []
        id_rows = []
        
        for entry in entries:
            media_id = str(uuid7())
            anilist_id = extract_external_id(entry["sources"], "anilist.co")
            
            media_rows.append({
                "id": media_id,
                "title_romaji": entry["title"],
                "media_type": "anime",  # all entries in this DB are anime
                "format": entry.get("type", "UNKNOWN").upper(),
                "status": entry.get("status", "UNKNOWN").lower(),
                "episode_count": entry.get("episodes"),
            })
            id_rows.append({
                "media_id": media_id,
                "anilist_id": int(anilist_id) if anilist_id else None,
                "mal_id": extract_external_id(entry["sources"], "myanimelist.net"),
                "kitsu_id": extract_external_id(entry["sources"], "kitsu.app"),
            })
        
        if dry_run:
            print(f"DRY RUN: Would insert {len(media_rows)} media entries")
            return
        
        # Bulk upsert
        stmt = pg_insert(MediaEntry).values(media_rows)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        await db.execute(stmt)
        
        stmt = pg_insert(MediaExternalIds).values(id_rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["anilist_id"],
            set_={"mal_id": stmt.excluded.mal_id}
        )
        await db.execute(stmt)
        await db.commit()
        
        print(f"✅ Seeded {len(media_rows)} anime entries")
        print("Next: run backfill worker to fetch full metadata from AniList")

if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    asyncio.run(seed(dry_run=dry_run))
```

## Run Instructions
```bash
# From project root
cd backend
python -m scripts.seed_anime_db          # full seed
python -m scripts.seed_anime_db --dry-run # preview only

# Then trigger AniList backfill
celery -A workers call workers.sync.backfill_all_anilist
```

Generate this script, adapting imports and model names to match the actual codebase.
