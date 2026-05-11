# ADR 041 — Auth/Setup Component Test Expansion Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 16.4 requires expanding auth/setup frontend tests so the hardening contracts from Phases 16.1–16.3 are reliably enforced over time.

Without explicit coverage requirements, validation and error-mapping regressions are likely during later UI iteration.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 16.4**.

## Decision
Adopt a mandatory auth/setup test matrix:

1. **Login page tests**
   - Empty submit validation.
   - Invalid input/disabled submit behavior.
   - In-flight submit lock.
   - Success redirect behavior.
   - 401/429/5xx mapping assertions.

2. **Register page tests**
   - Empty submit validation.
   - Invalid email handling.
   - Weak password handling.
   - Confirm-password mismatch handling.
   - In-flight submit lock.
   - Success redirect behavior.
   - 400/403/429/5xx mapping assertions.

3. **Setup bootstrap tests**
   - Empty submit validation.
   - Invalid input and confirm mismatch handling.
   - In-flight submit lock.
   - Success transition behavior.
   - 409 redirect behavior.
   - 429/5xx mapping assertions.

4. **Cross-cutting test quality rules**
   - Prefer user-facing assertions (visible messages/button disabled state/router transitions).
   - Avoid implementation-detail-only assertions where possible.
   - Keep test naming aligned with error mapping contracts.

5. **Verification baseline before completion**
   - Run relevant frontend test suite (`npx vitest run`).
   - Keep route guard smoke coverage passing alongside auth/setup tests.

## Consequences
**Good**:
- Protects hardened auth/setup UX from regression.
- Makes expected behavior explicit for future contributors.
- Reduces production friction in sign-in/sign-up/setup flows.

**Bad**:
- Increased test maintenance and runtime.
- Requires careful mocking strategy for auth API responses.

**Neutral**:
- No API/DB contract changes.
- No backend business-logic changes.
