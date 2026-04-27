# ADR 005 — Use QueryBuilder as the default read‑path in BaseRepository
**Status**: Proposed
**Date**: 2026-04-27

## Context
* The new `QueryBuilder` (added in Phase 4) provides a fluent, composable API for filtering, ordering, pagination, joins, grouping, etc.
* Only a handful of concrete repositories (`MediaRepository`, `UserRepository`) have been migrated to use it.
* `BaseRepository` still exposes raw `select()`/`where()` calls for its generic CRUD helpers (`get_by_id`, `list_all`, etc.).
* Maintaining two parallel query styles creates cognitive overhead, makes it easy to forget to apply global filters (e.g., soft‑delete), and hampers future cross‑cutting concerns (tenant scoping, audit‑logging).

## Decision
* **All SELECT‑type queries in every repository must be built through `QueryBuilder`.**
* `BaseRepository` will be refactored so that its generic read helpers (`get_by_id`, `list`, `filter`, `exists`, `count`, `paginate`) internally delegate to a `QueryBuilder` instance.
* The public API of `BaseRepository` stays the same (method signatures unchanged) – only the implementation changes.
* Write‑operations (`create`, `update`, `soft_delete`) remain as simple async SQLAlchemy calls because they are not composable queries.
* A **global soft‑delete filter** (`WHERE deleted_at IS NULL`) will be automatically applied by the builder (see ADR 006).

## Consequences
### Good
* Uniform data‑access surface – developers only need to learn one pattern.
* Central place to inject cross‑cutting concerns (soft‑delete, tenant ID, row‑level security, audit hooks).
* Easier to add new query features (e.g., `with_for_update`, `selectinload`) without touching every repository.

### Bad
* One‑time refactor effort across all repository files (≈ 15 files in the current codebase).
* Slight runtime overhead of constructing a builder object (negligible vs. DB latency).

### Neutral
* No impact on existing API contracts or external behaviour; only internal implementation changes.

## Acceptance Criteria
1. `BaseRepository.query()` returns a fresh `QueryBuilder` bound to the repository’s model.
2. `BaseRepository.get_by_id(id)` internally does `await self.query().filter(self.model.id == id).first()`.
3. `BaseRepository.list(offset, limit, order_by)` uses `self.query().order_by(*order_by).offset(offset).limit(limit).all()`.
4. All existing concrete repositories (`media_repository`, `user_repository`, `group_repository`, …) are updated to **remove** any direct `select()` usage and rely on the base helpers.
5. Unit tests (`test_base_repository_query_builder.py`) verify that the global soft‑delete filter is applied automatically.
6. Documentation (this ADR, layer‑boundary spec, and API docs) is updated accordingly.

## Related ADRs
* **ADR 006 – Global Soft‑Delete Policy** (adds automatic `deleted_at IS NULL` filter to the builder).
