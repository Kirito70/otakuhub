# Claude Code Instructions — OtakuHub

> This file extends AGENTS.md. Read AGENTS.md first.

## How Claude Should Work on This Project

### Before Starting Any Task
1. Read the relevant `docs/` file for the domain
2. Run `git status` to understand current state
3. Check for open Alembic revisions before touching DB: `alembic heads`
4. For frontend work, run `vue-tsc --noEmit` first to see baseline TS errors

### Preferred Workflow
- Always create a TODO list from the current `PROJECT-STATUS.md` phase/sub-phases before coding.
- Break large sub-phases into sub-tasks and track them explicitly.
- Move only one todo to `in_progress` at a time and update status continuously.
- Never mark a phase complete unless every sub-phase has implementation + verification evidence.

- Always propose a plan before writing code for tasks longer than ~30 lines
- Follow strict TDD: red → green → refactor
- Write/update tests before implementation when feasible; if not feasible due to legacy coupling, add failing regression tests immediately after reproducing bug
- After writing a new FastAPI endpoint, update `docs/api-spec.md`
- After writing a new DB migration, update `docs/database-schema.md`
- After a new Quasar page, update the route table in `docs/quasar-architecture.md`

### Frontend Form Validation Policy (Mandatory)
- Every frontend form must validate required fields and basic format constraints before API submission.
- Use Quasar primitives: `QForm`, `QInput` rules, and `lazy-rules`.
- Submit actions must be blocked when the form is invalid.
- Show actionable inline validation messages near each invalid field.
- Add/update Vitest tests for each form flow: empty submit, invalid format, inline errors, and successful submit.

### Custom Commands Available
- `/design-feature <name>` — ADR + data model + API contract + Pinia store shape
- `/review-pr` — Full code review: logic, types, tests, security, performance
- `/new-migration <name>` — Properly structured Alembic migration
- `/audit-security` — Security scan: auth, SQL injection, data exposure
- `/quasar-page <name>` — Scaffold a new Quasar page + Pinia store + tests
- `/seed-db` — Generate the DB seed script
- `/sync-worker <name>` — Create a Celery worker for a sync task
- `/next-phase` — Mark current sub-phase done, advance PROJECT-STATUS.md

### Code Review Checklist (use /review-pr)
- [ ] TypeScript strict — no `any`, no `as unknown as X` hacks
- [ ] `<script setup lang="ts">` on every component
- [ ] Pinia store used for shared state — no prop drilling beyond 2 levels
- [ ] All async: `isLoading`, `error`, `data` refs exposed from composable
- [ ] Quasar components used (QCard, QList, etc.) — not raw divs where Quasar has a component
- [ ] Responsive: `$q.screen` breakpoints used, not raw CSS media queries
- [ ] No direct AniList/MangaDex calls from frontend
- [ ] Axios interceptor handles 401 → token refresh
- [ ] Frontend forms enforce required/format validation before API calls
- [ ] Frontend form tests cover empty submit, invalid input, inline errors, and successful submit
- [ ] Backend: type hints complete, Pydantic v2 responses, repository pattern
- [ ] Migrations: downgrade() implemented, round-trip tested
- [ ] Tests present for new endpoints and new pages

### Context Always Relevant
- Frontend is Quasar 2.x with Vue 3 Composition API, TypeScript strict, Pinia, Axios
- Mobile: Capacitor 6 (wraps web build in native shell for Android/iOS)
- Desktop: Electron (wraps web build for Windows/Linux)
- The frontend NEVER calls AniList/MangaDex directly — always via FastAPI
- User tokens stored in `localStorage` with pinia-plugin-persistedstate (Electron/web)
  and Capacitor Preferences plugin on mobile native
