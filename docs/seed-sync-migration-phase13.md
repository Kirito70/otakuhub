# Phase 13.9 Migration Notes — Seed/Sync Entry Deprecations

## Canonical command path

All seed/sync execution is now backend-owned and must use:

- `otakuhub seed anime-offline`
- `otakuhub seed anilist`
- `otakuhub seed mangadex`
- `otakuhub seed jikan`
- `otakuhub seed all`

## Deprecated entrypoints

### 1) Root script shim
- Legacy: `python scripts/seed_database.py`
- Status: **Deprecated shim retained**
- Behavior: prints deprecation warning and delegates to `anime-offline` seed orchestration path.

### 2) Legacy CLI alias
- Legacy: `otakuhub seed run`
- Status: **Deprecated shim retained**
- Behavior: prints deprecation warning and delegates to `otakuhub seed anime-offline`.

### 3) Root `src/` package
- Status: **Deprecated namespace**
- Behavior: emits `DeprecationWarning` on import.
- Guidance: use `backend/src/` as source of truth and invoke backend via `otakuhub ...`.

## Usage inventory (Phase 13.9 check)

Observed in-repo references during migration:
- `docs/sync-pipeline.md` contained `otakuhub seed run` examples (updated).
- `backend/README.md` contained `otakuhub seed run` examples (updated).
- `scripts/seed_database.py` existed as standalone seed placeholder (replaced by shim).

No active backend orchestration code path uses root `scripts/seed_database.py` as canonical logic.
