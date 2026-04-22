# OtakuHub — Universal Rules (all files, always active)

## Project Context
OtakuHub is a FastAPI + Flutter monorepo. Small friend-group anime tracking platform.
Backend: Python/FastAPI/PostgreSQL. Frontend: Flutter (5 platforms from one codebase).

## Non-Negotiables
- Use async SQLAlchemy — never synchronous DB calls in async FastAPI routes
- UUID v7 primary keys on all new tables
- Pydantic v2 for all schemas — never raw dicts as API responses
- Riverpod 2.x for Flutter state — no setState in screens
- All external API calls (AniList, MangaDex) go through FastAPI, never from Flutter directly
- Soft deletes only on user content: set `deleted_at`, never hard DELETE

## Always Do
- Add type hints to every Python function
- Add error state + loading state handling to every Flutter async widget
- Use `Annotated[X, Depends()]` for FastAPI dependency injection
- Run `dart analyze` before reporting Flutter work as done
- Run `ruff check` + `mypy` before reporting Python work as done
