# ADR 038 — Login Page Hardening Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 16.1 focuses on hardening the login page UX and behavior so users get reliable validation, clear backend error feedback, and predictable loading/submit behavior.

Current auth flow exists, but hardening is needed to reduce silent failures and improve small-screen usability and accessibility consistency with Phase 15 design-system contracts.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 16.1**.

## Decision
Adopt the following login hardening contract:

1. **Client-side validation baseline**
   - `username` required (trimmed, non-empty).
   - `password` required (non-empty).
   - Submit remains disabled while invalid or in-flight.

2. **Submit lifecycle and idempotency UX**
   - First valid submit transitions form into loading state.
   - Duplicate submits are blocked while request is pending.
   - Submit button exposes deterministic label/state (e.g., "Signing in...").

3. **Backend error mapping policy**
   - `401` maps to actionable invalid-credentials message.
   - `429` maps to rate-limit guidance with retry hint.
   - `5xx/network` maps to retry-safe generic service message.
   - Inline field errors are reserved for client validation; auth failures shown as form-level banner.

4. **Post-login transition contract**
   - On success: persist tokens via auth store, hydrate user, navigate to authenticated landing route.
   - On failure: preserve entered username, clear password optional by security policy (implementation decision), restore non-loading controls.

5. **Testing requirements (TDD-aligned)**
   - Empty submit validation.
   - Invalid input/disabled submit behavior.
   - Loading-state lock preventing double submit.
   - Success path redirect.
   - 401/429/5xx mapping assertions.

## Consequences
**Good**:
- Fewer login retries caused by unclear failures.
- Better protection against accidental repeated submissions.
- Consistent auth UX across web/electron/mobile breakpoints.

**Bad**:
- Requires refactor of current login form wiring and tests.
- Slightly more frontend state complexity.

**Neutral**:
- No database schema changes.
- No new API endpoints; uses existing `/api/v1/auth/login` contract.
