# OtakuHub — GitHub Copilot Instructions

## Project Summary
OtakuHub is a private friend-group anime/manga/manhwa tracking app.
Backend: Python 3.12 + FastAPI + SQLAlchemy 2 async + PostgreSQL 16 + Celery + Redis.
Frontend: Flutter 3.x / Dart 3 — single codebase for web, Windows, Android, iOS, Linux.

## How to Build and Test
```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload

# Tests
pytest tests/ -v --asyncio-mode=auto

# Flutter
cd mobile
flutter pub get
dart run build_runner build --delete-conflicting-outputs
flutter run -d chrome   # web
flutter run -d windows  # Windows desktop
flutter test            # unit + widget tests
```

## Key Conventions
- Python: Pydantic v2, SQLAlchemy 2 async, repository pattern, ruff + mypy strict
- Dart: Riverpod 2 + riverpod_annotation, go_router, Dio, Freezed models
- DB: UUID v7 PKs, TIMESTAMPTZ UTC, soft deletes with deleted_at, Alembic migrations
- API: FastAPI routers → services → repositories; never raw dicts in responses
- Flutter: features/<name>/data/domain/presentation; AdaptiveScaffold for responsive

## Critical Rules for Code Generation
- Never call AniList/MangaDex API from Flutter — always via FastAPI backend
- Every FastAPI route needs auth dependency unless explicitly public
- All DB writes in async context managers with `async with session.begin()`
- Riverpod providers must handle loading + error states
- Use `selectinload()` for related data — avoid N+1 queries
