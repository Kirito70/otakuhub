# OtakuHub — GitHub Copilot Instructions

## Project Summary
OtakuHub is a private friend-group anime/manga/manhwa tracking app.
Backend: Python 3.12 + FastAPI + SQLAlchemy 2 async + PostgreSQL 16 + Celery + Redis.
Frontend (active): Flutter 3.x (Dart 3.x) — mobile, desktop, web, TV from one codebase.
Frontend (reference): Vue 3 + Vite + Tailwind (kept at `frontend/` for design patterns, NOT the active frontend).

## How to Build and Test
```bash
# Backend
cd backend
uv sync --extra dev
alembic upgrade head
uvicorn src.app.main:app --reload

# Backend tests
uv run pytest tests/ -v --asyncio-mode=auto

# Frontend (Flutter) — active
cd frontend/flutter
flutter pub get
flutter run                           # auto device
flutter run -d chrome                 # web
flutter run -d windows                # desktop
flutter test                          # all tests
flutter analyze                       # static analysis
flutter build apk                     # Android

# Frontend (Vue — reference only)
cd frontend
npm install        # not actively maintained
```

## Phase/Todo Enforcement
- Read `PROJECT-STATUS.md` before starting any implementation.
- Create an explicit todo checklist for all sub-phases/subtasks in scope.
- Complete and verify sub-phases one-by-one; do not skip ahead.
- Update `PROJECT-STATUS.md` only after verification.

## Key Conventions

### Frontend (Flutter — active)
- Feature-first: `lib/features/<name>/` with models, providers, screens, widgets
- Riverpod 2.x for state — NotifierProvider for complex, FutureProvider for async
- `freezed` + `json_serializable` for all data models
- Dio with auth interceptor for all HTTP — no `http` package
- GoRouter with ShellRoute for adaptive layouts — auth guard redirect
- Responsive: `LayoutBuilder` + breakpoints (600/1024)
- TV: `Focus` widget for D-pad navigation
- All forms: `Form` + `TextFormField` validators before API submission

### Backend (FastAPI / Python)
- Pydantic v2, SQLAlchemy 2 async, repository pattern, ruff + mypy strict
- All DB writes in `async with session.begin()`
- Celery tasks: idempotent, `acks_late=True`, `max_retries=3`

### Database
- UUID v7 PKs, TIMESTAMPTZ UTC, soft deletes, Alembic migrations

## Critical Rules for Code Generation
- NEVER call AniList/MangaDex/Jikan API from the frontend — always via FastAPI backend
- NEVER use `dynamic` in Dart — always explicit types
- Every FastAPI route needs auth dependency unless explicitly public
- All DB writes in async context managers with `async with session.begin()`
- The Vue 3 code in `frontend/` is REFERENCE ONLY — do not modify it for Flutter work
