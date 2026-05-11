# ADR 075 — Profile Page Test Coverage Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 22.4 defines required test coverage for Profile frontend pages (overview, edit, account/security) to preserve behavior contracts before final polish/deploy phase.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 22.4**.

## Decision
1. Maintain profile-page test matrix covering:
   - Overview tab,
   - Edit Profile tab,
   - Account & Security tab.
2. Each tab must verify loading/empty/error/success states where applicable.
3. Edit tab coverage includes form validation, save success/failure, in-flight disable, and retry.
4. Account/Security coverage includes password validation, confirmation-gated actions, in-flight disable, and failure mapping.
5. Navigation coverage includes profile sub-tab action routing.
6. Prefer user-visible assertions over implementation details.
7. Verification baseline: run `npx vitest run` for profile suites before phase completion.

## Consequences
**Good**: Prevents regressions across core profile/account flows.
**Bad**: Additional test maintenance overhead.
**Neutral**: No API or DB schema changes.
