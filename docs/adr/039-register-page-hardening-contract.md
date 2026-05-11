# ADR 039 — Register Page Hardening Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 16.2 focuses on hardening the registration flow so first-run and admin-managed onboarding paths remain predictable, validated, and secure from a UX standpoint.

The register page already exists, but requires stricter validation and clearer conflict/error feedback to reduce failed attempts and confusion.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 16.2**.

## Decision
Adopt the following registration hardening contract:

1. **Validation contract**
   - `username`: required, trimmed, non-empty.
   - `email`: required, valid email format.
   - `password`: required, minimum-strength baseline (length + complexity policy set by frontend rules aligned with backend acceptance).
   - `confirmPassword`: required, must exactly match `password`.
   - Submit disabled while invalid or request is in-flight.

2. **Submit lifecycle**
   - Single in-flight request allowed; block repeated submits.
   - Loading state clearly reflected in CTA text/state.

3. **Backend error mapping policy**
   - `400` with conflict semantics (username/email already used) => actionable user-facing guidance.
   - `403` (register disallowed post-bootstrap) => explain admin-managed account creation policy.
   - `429` => retry-later guidance.
   - `5xx/network` => generic retry-safe service message.
   - Field-level frontend errors remain client-validation-only.

4. **Success flow**
   - On successful register, follow auth-store contract (persist tokens when returned, hydrate user, and navigate to authenticated landing).
   - Preserve non-sensitive user input on recoverable failures; clear sensitive fields per implementation policy.

5. **Testing requirements (TDD-aligned)**
   - Empty submit and per-field validation.
   - Invalid email format and weak password handling.
   - Confirm-password mismatch behavior.
   - In-flight disabled submit / double-submit prevention.
   - Success redirect.
   - 400/403/429/5xx mapping checks.

## Consequences
**Good**:
- Clearer onboarding outcomes and lower frustration during account creation.
- Better alignment with bootstrap lock policy introduced in Phase 12.
- Reduced accidental duplicate submissions.

**Bad**:
- Additional frontend validation/test complexity.
- Requires harmonization with backend validation messages to avoid contradictory wording.

**Neutral**:
- No DB schema changes.
- No new API endpoints.
