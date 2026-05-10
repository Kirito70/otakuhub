---
paths:
  - "backend/**"
  - "scripts/**"
---
# Backend Rules (Python / FastAPI)

## Layer Architecture
```
backend/
  routers/      ← HTTP layer only: parse input, call service, return response
  services/     ← Business logic: orchestrate repositories, apply rules
  repositories/ ← DB layer only: SQLAlchemy queries, no business logic
  models/       ← SQLAlchemy ORM models
  schemas/      ← Pydantic v2 request/response models
  workers/      ← Celery tasks (sync pipeline, notifications)
  core/         ← Config, database session, auth utilities
```

## Coding Patterns
- Route handlers: max ~20 lines. If longer, extract to service.
- Service methods: pure business logic, return domain objects or Pydantic schemas
- Repository methods: return SQLAlchemy model instances or scalars, never HTTP types
- Use `select()` + `scalars()` + `first()` / `all()` — not deprecated `Query` API
- Eager load related data with `selectinload()` to avoid N+1
- Celery tasks: idempotent by design — safe to retry on failure

## Error Handling
- User not found → 404 with `detail: "User not found"`
- Duplicate unique key → 409 Conflict
- Auth failure → 401 or 403 depending on context
- External API failure (AniList/MangaDex) → 503 with retry hint in detail
- Never expose internal stack traces in 5xx responses

## Database Rules
- Always use `async with db.begin()` for write operations (auto-rollback on exception)
- Never call `db.commit()` manually inside a repository — let the service or router context manage it
- Migrations: `alembic revision --autogenerate -m "descriptive_name"`; always review before applying
- Add `__table_args__ = (Index(...), )` for all columns used in WHERE clauses

## Testing
- Every router needs at minimum: success case, auth failure case, not-found case
- Use `pytest-asyncio` with `asyncio_mode = "auto"` in `pytest.ini`
- Use a separate test database; never run tests against dev/prod DB
- Fixture for authenticated user: `auth_headers` fixture returns Bearer token headers
