# Claude Code Instructions — OtakuHub

> This file extends AGENTS.md. Read AGENTS.md first.

## How Claude Should Work on This Project

### Before Starting Any Task
1. Read the relevant `docs/` file for the domain you're working in
2. Run `git status` to understand current state
3. Check for open Alembic revisions before touching the DB: `alembic heads`
4. For Flutter work, run `flutter analyze` first to see baseline issues

### Preferred Workflow
- Always propose a plan before writing code for tasks longer than ~30 lines
- Write tests alongside implementation — not as a separate step
- After writing a new FastAPI endpoint, also update `docs/api-spec.md`
- After writing a new DB migration, add the table/column to `docs/database-schema.md`

### Custom Commands Available
Use these slash commands (defined in `.claude/commands/`):
- `/design-feature <name>` — Generate an ADR + data model + API contract for a new feature
- `/review-pr` — Full code review: logic, types, tests, security, performance
- `/new-migration <name>` — Create a properly structured Alembic migration
- `/audit-security` — Security scan: auth, SQL injection, data exposure, prompt injection
- `/spec-endpoint <route>` — Write OpenAPI spec for a given route
- `/seed-db` — Generate the DB seed script for the anime-offline-database import
- `/flutter-screen <name>` — Scaffold a new Flutter feature screen with Riverpod provider
- `/sync-worker <name>` — Create a Celery worker for a new sync task

### Code Review Checklist (use /review-pr)
When reviewing, check ALL of these:
- [ ] Type annotations complete and correct
- [ ] No N+1 queries (check for missing `selectinload`/`joinedload`)
- [ ] Pydantic response models used (no raw dict returns)
- [ ] Auth dependency on all protected routes
- [ ] Rate limiting considered for sync/external API calls
- [ ] Soft delete respected (no hard DELETEs on user data)
- [ ] Migration is reversible (has `downgrade()` implemented)
- [ ] Flutter: no `setState` in screen files; Riverpod only
- [ ] Flutter: loading + error states handled in all async widgets
- [ ] No secrets or API keys in code

### Architecture Decision Records
When making a significant architectural choice, create an ADR in `docs/adr/`:
```
docs/adr/
  001-database-uuid-v7.md
  002-anilist-as-primary-source.md
  003-riverpod-state-management.md
  ...
```
ADR template: Title, Status, Context, Decision, Consequences.

### Context Always Relevant
- The anime metadata DB is seeded from `manami-project/anime-offline-database`
- AniList IDs are the canonical foreign keys across the system
- MangaDex IDs supplement manga/manhwa entries
- User tracking data (progress, ratings, lists) is entirely in our DB — not synced back to AniList
- The Flutter app talks ONLY to our FastAPI backend, never to external APIs directly
