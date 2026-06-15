# OtakuHub

Private friend-group anime/manga/manhwa tracking + social platform.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy async, Alembic, Celery, Redis, PostgreSQL 16
- **Frontend (active):** Flutter 3 (Dart 3) — mobile, desktop, web, TV
- **Frontend (reference):** Vue 3 + Vite + Tailwind (kept at `frontend/`)
- **Infra:** Docker Compose + Nginx TLS reverse proxy

---

## Monorepo Structure

```text
otakuhub/
├── backend/      # FastAPI app + Alembic + Celery workers
├── frontend/     # Vue 3 reference app (kept for design/UX patterns)
│   └── flutter/  # Flutter app (active — mobile, desktop, web, TV)
├── infra/        # docker compose + nginx + cert mounts
├── docs/         # architecture and ADRs
└── scripts/      # utility scripts
```

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Node.js 20+ and npm
- Docker Desktop (for compose flows)

---

## 1) Local Development Setup (non-docker)

### Backend

```bash
cd backend
cp .env.example .env
# set required security values in .env before startup:
# - JWT_SECRET (strong random value, 64+ chars recommended)
# - CORS_ORIGINS (explicit CSV; wildcard '*' is rejected)
uv sync --extra dev
uv run alembic upgrade head
uv run otakuhub-dev
```

Backend will be available at `http://localhost:8000`.

### Worker (separate terminal)

```bash
cd backend
uv run otakuhub celery worker --loglevel info --queue sync
```

### Frontend (Flutter)

```bash
cd frontend/flutter
cp .env.example .env  # or create with API_BASE_URL
flutter pub get
flutter run            # auto-select device
flutter run -d chrome  # web
flutter run -d windows # desktop
```

Flutter app will auto-launch on the selected device.

---

## 2) Docker Compose (Production-style local verification)

> Uses: `infra/docker-compose.prod.yml`

### 2.1 Prepare env file

`infra/.env.prod.test` is included for local validation. If needed, duplicate/edit it:

```bash
cp infra/.env.prod.test infra/.env.prod.local
```

Then use `--env-file infra/.env.prod.local` in commands below.

### 2.2 Generate local TLS certs for Nginx

From repo root:

```bash
docker run --rm -v "${PWD}/infra/certs:/certs" alpine/openssl \
  req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /certs/key.pem -out /certs/cert.pem -subj "/CN=localhost"
```

### 2.3 Start stack

```bash
docker compose --env-file "infra/.env.prod.test" -f "infra/docker-compose.prod.yml" up -d --build
```

### 2.4 Verify services

```bash
docker compose --env-file "infra/.env.prod.test" -f "infra/docker-compose.prod.yml" ps
curl -k https://localhost/health
```

Expected health response:

```json
{"status":"healthy","service":"OtakuHub"}
```

### 2.5 Stop stack

```bash
docker compose --env-file "infra/.env.prod.test" -f "infra/docker-compose.prod.yml" down -v
```

---

## 3) Seed / Sync Pipeline

### Prerequisites

Before running seed commands, make sure PostgreSQL is running and reachable:

```bash
# Check DB connection
uv run otakuhub health
```

If you get a password error for local Docker Postgres:

```bash
# Enter the postgres container and set the password to match your .env
docker exec -it <container-name> psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'admin';"
```

### Step 1 — Seed anime-offline-database

Downloads ~40k anime entries from the [anime-offline-database](https://github.com/manami-project/anime-offline-database) project (GitHub Releases) and upserts them into `media_entries` + `media_external_ids`.

```bash
cd backend
uv run otakuhub seed anime-offline   # 40k entries, ~2 min
```

Expected output:
```
source=anime-offline job_id=... status=completed processed_items=40921 failed_items=0
```

### Step 2 — Backfill AniList metadata

Enriches seeded entries with rich AniList metadata (synopsis, scores, cover images, episodes, genres, studios, tags, air dates, seasons). Paced by AniList rate limit (~90 req/min).

```bash
cd backend
uv run otakuhub seed anilist         # enriches entries with anilist_id, ~7 min
```

### Step 3 — (Optional) Seed all sources in sequence

Runs anime-offline → anilist → mangadex in order:

```bash
cd backend
uv run otakuhub seed all
```

### Step 4 — Weekly refresh (background worker)

Keeps airing-status and scores up-to-date:

```bash
cd backend
uv run otakuhub celery beat --loglevel info
```

### Seed Notes

- **Idempotent**: Re-running the same seed command skips already-inserted entries (checks by `anilist_id`, then `mal_id`, then `anidb_id`, then title).
- **If re-seed is needed**, truncate the tables first:
  ```bash
  docker exec -it <container> psql -U postgres -d otakuhub \
    -c "TRUNCATE mediaexternalids, media_entries, syncjob CASCADE;"
  ```
- The AniList backfill improves search quality, enables score-based sorting, and populates genre/tag/studio data used by the Flutter frontend.

---

## 4) Quality Gates

### Backend

```bash
cd backend
uv run ruff check src/
uv run mypy src/ --strict
uv run pytest tests/ --asyncio-mode=auto
```

### Frontend (Flutter)

```bash
cd frontend/flutter
flutter analyze
flutter test
flutter build apk       # Android
flutter build web       # Web
flutter build windows   # Windows desktop
```

---

## 5) Key Docs

- `PROJECT-STATUS.md` — single source of truth for current phase/sub-phase
- `docs/backend-architecture.md`
- `docs/flutter-architecture.md` (primary frontend)
- `docs/frontend-architecture.md` (Vue reference)
- `docs/database-schema.md`
- `docs/api-spec.md`
- `docs/adr/` — architecture decision records

---

## 6) Notes

- AniList ID is the canonical external cross-reference key.
- Frontend must not call AniList/MangaDex directly; all calls go through FastAPI.
- User progress/tracking data is stored only in OtakuHub DB.
- Auth hardening in current baseline:
  - bcrypt/passlib password hashing with legacy SHA-256 verify-and-upgrade path
  - refresh-token replay detection revokes all active user refresh tokens
  - startup fails fast on insecure JWT secret or wildcard CORS
