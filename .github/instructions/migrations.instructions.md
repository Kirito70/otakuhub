---
applyTo: "alembic/versions/**"
---
# Alembic Migration Copilot Instructions

Every migration MUST implement both `upgrade()` AND `downgrade()`.
Use `server_default=sa.text("uuid_generate_v7()")` for UUID PKs — autogenerate does not add this.
Create PostgreSQL ENUM types with `op.execute("CREATE TYPE...")` BEFORE the table that uses them.
Add GIN indexes manually — autogenerate does not generate them.
Use `sa.TIMESTAMP(timezone=True)` for all timestamp columns.
Soft-delete pattern: add `deleted_at TIMESTAMP(timezone=True)` nullable column, never drop rows.
Test: after writing the migration, run upgrade then downgrade then upgrade again — all must succeed.
