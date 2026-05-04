# OtakuHub — GitHub Copilot Instructions

## Project Summary
OtakuHub is a private friend-group anime/manga/manhwa tracking app.
Backend: Python 3.12 + FastAPI + SQLAlchemy 2 async + PostgreSQL 16 + Celery + Redis.
Frontend: Quasar 2.x (Vue 3 + Vite + TypeScript strict) — targets web, Electron desktop (Windows/Linux), and Capacitor mobile (Android/iOS) from one codebase.

## How to Build and Test
```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# Backend tests
pytest tests/ -v --asyncio-mode=auto

# Frontend dev server
cd frontend
npm install
quasar dev

# Frontend type check
vue-tsc --noEmit

# Frontend build — all targets
quasar build              # web SPA
quasar build -m pwa       # PWA
quasar build -m electron  # desktop (Windows + Linux)
quasar build -m capacitor -T android  # Android
```

## Key Conventions

### Frontend (Quasar / Vue 3)
- `<script setup lang="ts">` on every component
- Pinia stores in `src/stores/` — one per domain
- Composables in `src/composables/use<Name>.ts`
- HTTP via Axios boot file (`src/boot/axios.ts`) — never `fetch()` or raw `axios`
- Typed routes — named routes only, no raw path strings
- `QVirtualScroll` for lists > 100 items
- `$q.screen` for responsive breakpoints
- `$q.notify()` for toast notifications

### Backend (FastAPI / Python)
- Pydantic v2, SQLAlchemy 2 async, repository pattern, ruff + mypy strict
- All DB writes in `async with session.begin()`
- Celery tasks: idempotent, `acks_late=True`, `max_retries=3`

### Database
- UUID v7 PKs, TIMESTAMPTZ UTC, soft deletes, Alembic migrations

## Critical Rules for Code Generation
- NEVER call AniList/MangaDex/Jikan API from the frontend — always via FastAPI backend
- NEVER use `any` in TypeScript
- NEVER use Options API — always `<script setup lang="ts">`
- Every FastAPI route needs auth dependency unless explicitly public
- All DB writes in async context managers with `async with session.begin()`
