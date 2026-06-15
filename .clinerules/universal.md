# OtakuHub — Universal Rules (all files, always active)

## Project Context
OtakuHub is a FastAPI + Flutter monorepo. Small friend-group anime tracking platform.
Backend: Python/FastAPI/PostgreSQL. Frontend (active): Flutter 3 (Dart 3). Frontend (reference): Vue 3 + Tailwind (in `frontend/`).

## Non-Negotiables
- Use async SQLAlchemy — never synchronous DB calls in async FastAPI routes
- UUID v7 primary keys on all new tables
- Pydantic v2 for all schemas — never raw dicts as API responses
- Riverpod for all shared Flutter state — no prop drilling beyond 2 levels (except in reference Vue code)
- All external API calls (AniList, MangaDex) go through FastAPI, never from the frontend
- Soft deletes only on user content: set `deleted_at`, never hard DELETE
- Dart explicit types — no `dynamic`

## Always Do
- Add type hints to every Python function
- Use `ConsumerWidget` / `ConsumerStatefulWidget` for screen widgets
- Use `freezed` models with `fromJson`/`toJson`
- Run `flutter analyze` before reporting frontend work as done
- Run `ruff check` + `mypy` before reporting Python work as done
- The Vue code in `frontend/` is reference-only — do not modify it
