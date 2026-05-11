# ADR 074 — Profile Account & Security Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 22.3 defines the Profile Account & Security tab behavior so users can manage password and session-safety controls with clear validation and risk-aware feedback.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 22.3**.

## Decision
1. Account & Security tab uses existing authenticated account-security endpoint contracts (password/session controls) where available.
2. State includes security form(s), `isLoading`, action-specific saving state, `error`, and success status.
3. Password-change flow validates required fields, confirm-match, and strength baseline before submit.
4. Session actions (e.g., logout-all/revoke session where supported) require explicit confirmation and actionable success/failure feedback.
5. Submit/actions disabled while in-flight to prevent duplicate mutations.
6. Security-sensitive messages avoid over-disclosing backend internals while still guiding user recovery.
7. Responsive behavior preserves critical action visibility and confirmation affordances across xs/sm/md+.
8. Tests cover validation, successful security updates, failure mapping, in-flight disable, confirmation flows, and retry behavior.

## Consequences
**Good**: Stronger user-facing account safety controls and clearer security UX.
**Bad**: Additional sensitive-state/confirmation handling complexity.
**Neutral**: No API or DB schema changes introduced by this contract.
