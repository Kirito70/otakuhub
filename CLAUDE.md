# Claude Code Instructions — OtakuHub

> This file extends AGENTS.md. Read AGENTS.md first.

## How Claude Should Work on This Project

### Before Starting Any Task
1. Read the relevant `docs/` file for the domain
2. Run `git status` to understand current state
3. Check for open Alembic revisions before touching DB: `alembic heads`
4. For frontend work, run `flutter analyze` first to see baseline errors

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
- After a new Flutter screen, update the route table in `docs/flutter-architecture.md`

### Frontend Form Validation Policy (Mandatory)
- Every frontend form must validate required fields and basic format constraints before API submission.
- Use Flutter `Form` + `TextFormField` validators.
- Submit actions must be blocked when the form is invalid.
- Show actionable inline validation messages near each invalid field.
- Add/update `flutter_test` tests for each form flow: empty submit, invalid format, inline errors, and successful submit.

### Custom Commands Available
- `/design-feature <name>` — ADR + data model + API contract + Flutter provider/state shape
- `/review-pr` — Full code review: logic, types, tests, security, performance
- `/new-migration <name>` — Properly structured Alembic migration
- `/audit-security` — Security scan: auth, SQL injection, data exposure
- `/flutter-page <name>` — Scaffold a new Flutter screen + Riverpod provider + tests
- `/seed-db` — Generate the DB seed script
- `/sync-worker <name>` — Create a Celery worker for a sync task
- `/next-phase` — Mark current sub-phase done, advance PROJECT-STATUS.md

### Code Review Checklist (use /review-pr)
- [ ] Dart strict types — no `dynamic`, no `as` casts without comments
- [ ] Feature-first structure: `lib/features/<name>/` with models, providers, screens, widgets
- [ ] Riverpod used for shared state — no prop drilling beyond 2 levels
- [ ] All async: Provider patterns for loading/error/data states
- [ ] Dio for HTTP — not `http` package directly
- [ ] `freezed` for models — not hand-written fromJson with error-prone null handling
- [ ] Responsive: `LayoutBuilder` + breakpoints (600/1024), not hardcoded sizes
- [ ] TV: Focus widget for D-pad navigation on all interactive elements
- [ ] No direct AniList/MangaDex calls from frontend
- [ ] Dio interceptor handles 401 → token refresh
- [ ] Frontend forms enforce required/format validation before API calls
- [ ] Frontend form tests cover empty submit, invalid input, inline errors, and successful submit
- [ ] Backend: type hints complete, Pydantic v2 responses, repository pattern
- [ ] Migrations: downgrade() implemented, round-trip tested
- [ ] Tests present for new endpoints and new screens

### Context Always Relevant
- Primary frontend is Flutter 3.x with Dart 3.x, Riverpod 2.x, GoRouter, Dio
- Targets: mobile (Android/iOS), desktop (Windows/Mac/Linux), web, TV (Android TV/Fire TV), tablet
- Vue 3 reference code lives in `frontend/` for design/UX reference only — do not modify it
- The frontend NEVER calls AniList/MangaDex directly — always via FastAPI
- User tokens stored in `flutter_secure_storage` (mobile/desktop)
- TV needs special Focus widget consideration — test with remote D-pad emulation
