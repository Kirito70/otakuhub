# ADR 032 — First-Run Super Admin Bootstrap Flow
**Status**: Accepted
**Date**: 2026-05-06

## Context
OtakuHub currently lacks a safe first-run setup flow for creating the initial privileged account.
Without this, first-user creation either depends on open public registration or manual DB edits.
For a private friend-group app, we need a one-time initialization path that is simple, explicit,
and closes itself after setup is complete.

## Project Status check
To check status of the project and know about its phase always refer to PROJECT-STATUS.md file at root of the project and once phase or sub phase is completed always update the project status.

## Decision
We will introduce a dedicated setup contract:

1. `GET /api/v1/setup/status` returns `{ setup_required: boolean }`.
2. `POST /api/v1/setup/bootstrap-admin` creates the first user as `is_admin=True`.
3. Bootstrap endpoint is one-time only and returns `409` once setup is already complete.
4. Public `POST /api/v1/auth/register` is disabled after setup and returns `403`.
5. New user creation after setup is via `POST /api/v1/users` and requires admin auth.
6. Frontend router checks setup status and redirects to `/setup` until bootstrap finishes.

Security/race handling:
- We enforce a setup-required precheck and return conflict if already initialized.
- We catch DB integrity conflicts on bootstrap commit and convert to `409` to reduce race impact.

## Consequences
**Good**:
- No manual DB edits needed to initialize an environment.
- Public signups are closed after first-run bootstrap.
- User provisioning becomes explicitly admin-governed.

**Bad**:
- Adds a setup-specific public endpoint and one extra routing branch.
- Requires frontend guard logic and setup UX maintenance.

**Neutral**:
- Keeps existing `users.is_admin` model; no schema migration required for this phase.
