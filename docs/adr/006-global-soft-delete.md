# ADR 006 — Global Soft‑Delete Filter in QueryBuilder
**Status**: Proposed
**Date**: 2026-04-27

## Context
* Many tables contain a nullable ``deleted_at`` timestamp for soft‑deletion.
* Currently each repository must remember to add ``.filter(Model.deleted_at.is_(None))`` manually.
* Forgetting this filter leads to leaked deleted rows in UI and API responses.

## Decision
* The ``QueryBuilder`` will automatically inject ``WHERE deleted_at IS NULL`` for **all** models that have a ``deleted_at`` column.
* The filter can be overridden (e.g., for admin “view‑deleted” endpoints) by calling ``builder.with_deleted()`` which disables the automatic clause.

## Consequences
* **Good** – Guarantees consistent soft‑delete handling without extra code.
* **Bad** – Slightly more complex builder implementation (needs reflection on model columns).
* **Neutral** – Existing admin endpoints can still opt‑out via ``with_deleted()``.

## Acceptance Criteria
1. ``QueryBuilder`` inspects ``self.model.__table__.c`` for a ``deleted_at`` column on construction.
2. By default the generated SELECT includes ``WHERE deleted_at IS NULL``.
3. ``builder.with_deleted()`` returns a new builder instance with the filter removed.
4. Unit tests cover both default and overridden behaviour.

---
