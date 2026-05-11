# ADR 040 — Setup Bootstrap Page Hardening Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 16.3 hardens the one-time setup bootstrap page used to create the first super admin. This flow is security-sensitive because it is only valid before bootstrap completion and must handle race/idempotency behavior cleanly.

Phase 12 introduced backend bootstrap and setup status endpoints; this phase formalizes robust frontend behavior for those constraints.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 16.3**.

## Decision
Adopt the following setup page hardening contract:

1. **Form validation baseline**
   - Required: username, email, password, confirm password.
   - Email format validation.
   - Password minimum-strength baseline aligned with register policy.
   - Confirm password must match exactly.

2. **One-time flow handling**
   - Page should only be reachable when `setup_required=true` from setup status/bootstrap guard.
   - If backend returns `409` (already initialized), immediately transition user to login route with explanatory notice.

3. **Submit lifecycle safety**
   - Single in-flight submit lock; prevent duplicate POST attempts.
   - Loading state and deterministic CTA label during submit.
   - Restore interactivity on failure.

4. **Error mapping policy**
   - `409` => setup already completed message + redirect guidance.
   - `429` => retry-later message.
   - `5xx/network` => retry-safe service unavailable message.
   - Field-level messages remain for client validation only.

5. **Post-success transition**
   - On success, persist auth state if tokens returned by bootstrap endpoint contract.
   - Route to authenticated landing when session is established; otherwise route to login with success banner.

6. **Testing requirements (TDD-aligned)**
   - Empty/invalid input validation cases.
   - Confirm mismatch handling.
   - In-flight submit lock.
   - Success transition behavior.
   - 409/429/5xx mapping and redirect behavior.

## Consequences
**Good**:
- Safer and clearer first-run setup UX.
- Strong alignment with backend one-time bootstrap guarantees.
- Reduces confusion when setup has already been completed by another actor.

**Bad**:
- Additional branching/redirect logic in setup page and route guard integration.
- Extra tests and error-state maintenance burden.

**Neutral**:
- No DB schema changes.
- No new API endpoints.
