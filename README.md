# OtakuHub

Private friend-group anime/manga/manhwa tracking + social platform.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy async, Alembic, Celery, Redis, PostgreSQL 16
- **Frontend:** Quasar 2 (Vue 3 + TypeScript)
- **Infra:** Docker Compose + Nginx TLS reverse proxy

---

## Monorepo Structure

```text
otakuhub/
├── backend/      # FastAPI app + Alembic + Celery workers
├── frontend/     # Quasar app (web/electron/capacitor)
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

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npx quasar dev
```

Frontend will be available at `http://localhost:9000` (Quasar default).

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

## 3) Quality Gates

### Backend

```bash
cd backend
uv run ruff check src/
uv run mypy src/ --strict
uv run pytest tests/ --asyncio-mode=auto
```

### Frontend

```bash
cd frontend
npm run -s typecheck
npm run -s test -- --run
npx quasar build
```

---

## 4) Key Docs

- `PROJECT-STATUS.md` — single source of truth for current phase/sub-phase
- `docs/backend-architecture.md`
- `docs/quasar-architecture.md`
- `docs/database-schema.md`
- `docs/api-spec.md`
- `docs/adr/` — architecture decision records

---

## Notes

- AniList ID is the canonical external cross-reference key.
- Frontend must not call AniList/MangaDex directly; all calls go through FastAPI.
- User progress/tracking data is stored only in OtakuHub DB.
