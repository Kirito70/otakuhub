# ADR 007 — Auth & Group Feature Design
**Status**: Proposed
**Date**: 2026-04-27

## Context
* OtakuHub needs a private‑group authentication system (JWT) and a lightweight friend‑group model.
* Existing code already has JWT utilities (`core/auth.py`) and a `User` model with soft‑delete.
* New tables (`groups`, `group_members`) will be added, both supporting soft‑delete on `groups`.
* All read operations must go through the `QueryBuilder` (ADR 005) which automatically filters out soft‑deleted rows (ADR 006).

## Decision
* Implement a **RESTful** set of endpoints under `/api/v1/auth` and `/api/v1/groups`.
* Use **Pydantic v2** request/response schemas (`schemas/auth.py`, `schemas/group.py`).
* **Auth flow**: login → issue access + refresh tokens; refresh → rotate refresh token; logout → revoke token.
* **Group flow**: CRUD for groups, member add/remove, list groups (owner‑only for private groups, public list for public groups).
* Enforce **role‑based access** (`owner`, `admin`, `member`). Only owners can delete groups; owners/admins can add/remove members.
* Apply **rate limiting** (5 req/s per IP for auth, 2 req/s per user for group mutations) via existing `core/rate_limiter.py`.
* All SELECT queries use `self.query()` → soft‑delete filter automatically applied.
* Write operations (`create`, `update`, `soft_delete`) remain direct async SQLAlchemy calls in the base repository.

## Consequences
### Good
* Consistent data‑access pattern across the whole codebase.
* Centralised soft‑delete handling prevents accidental exposure of deleted groups.
* Clear separation of concerns – routers only validate & delegate, services hold business rules, repositories handle DB.
* Rate limiting mitigates credential‑stuffing and abuse of group mutation endpoints.
### Bad
* Slight increase in code size (new services, routers, schemas).
* Need to maintain two token tables (`refresh_tokens`) and ensure proper revocation.
### Neutral
* No impact on existing media‑tracking features; they continue to use the same repository pattern.

## Acceptance Criteria
1. **Authentication**
   - `POST /auth/login` returns `TokenResponse` on valid credentials, 401 otherwise.
   - `POST /auth/refresh` validates refresh token, rotates it, returns new `TokenResponse`.
   - `POST /auth/logout` revokes the current refresh token.
2. **Group Management**
   - `GET /groups` returns paginated `GroupSummary` for groups the user belongs to.
   - `POST /groups` creates a group; owner becomes the requesting user.
   - `GET /groups/{group_id}` returns `GroupDetail` (owner‑only for private groups).
   - `PATCH /groups/{group_id}` updates allowed fields; only owner/admin can edit.
   - `DELETE /groups/{group_id}` soft‑deletes the group; only owner can delete.
   - `POST /groups/{group_id}/members` adds a member; only owner/admin can add.
   - `DELETE /groups/{group_id}/members/{user_id}` removes a member; only owner/admin can remove.
3. **Soft‑Delete** – `Group.deleted_at` is set on delete; queries automatically exclude rows where it is not NULL.
4. **Rate Limiting** – enforced as described in the API spec.
5. **Tests** – unit tests for services, integration tests for routers, repository test confirming soft‑delete filter.
6. **Documentation** – ADR 007 added, API spec updated, architecture doc notes added.

---
