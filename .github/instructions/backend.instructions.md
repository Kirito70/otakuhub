---
applyTo: "backend/**"
---
# Backend-Specific Copilot Instructions

Use async SQLAlchemy 2 with `AsyncSession`. Import pattern:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
```

Repository pattern: all DB queries in `repositories/`, services call repositories, routers call services.
Return Pydantic schemas from routers — never SQLAlchemy model instances directly.
Use `Annotated[AsyncSession, Depends(get_db)]` for DB dependency injection.
Every write operation: `async with session.begin(): ...` for auto-rollback.
Celery tasks in `workers/` — all tasks must be idempotent and handle retries.
