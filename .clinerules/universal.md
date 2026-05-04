# OtakuHub — Universal Rules (all files, always active)

## Project Context
OtakuHub is a FastAPI + Quasar monorepo. Small friend-group anime tracking platform.
Backend: Python/FastAPI/PostgreSQL. Frontend: Quasar (Vue 3 + TypeScript) — web, Electron desktop, Capacitor mobile.

## Non-Negotiables
- Use async SQLAlchemy — never synchronous DB calls in async FastAPI routes
- UUID v7 primary keys on all new tables
- Pydantic v2 for all schemas — never raw dicts as API responses
- Pinia for all shared frontend state — no prop drilling beyond 2 levels
- All external API calls (AniList, MangaDex) go through FastAPI, never from the frontend
- Soft deletes only on user content: set `deleted_at`, never hard DELETE
- TypeScript strict mode — no implicit `any`

## Always Do
- Add type hints to every Python function
- Use `<script setup lang="ts">` on every Vue component
- Use `isLoading`, `error`, `data` pattern in every async Pinia store action
- Run `vue-tsc --noEmit` before reporting frontend work as done
- Run `ruff check` + `mypy` before reporting Python work as done
