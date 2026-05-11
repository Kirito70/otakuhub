# ADR 064 — Watch Party Create Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 20.2 defines the Watch Party Create tab behavior so users can schedule sessions with valid date/time and link inputs, while minimizing scheduling mistakes.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 20.2**.

## Decision
1. Create tab uses existing authenticated watch-party create endpoint contract(s).
2. Form state includes media selection/context, title, scheduled datetime, optional stream/sync URLs, notes, `isLoading`, and form-level error.
3. Validation enforces required scheduling fields and basic URL format checks for stream/sync links.
4. Submit is disabled while invalid or request is in-flight; duplicate submissions are blocked.
5. Success transitions to watch-party detail/upcoming context with confirmation feedback.
6. Failure maps backend validation/policy errors to actionable form-level messages.
7. Loading/empty helper behavior follows shared primitive patterns.
8. Tests cover empty/invalid submit, URL validation, in-flight submit lock, success transition, and backend error mapping.

## Consequences
**Good**: More reliable watch-party scheduling with fewer invalid submissions.
**Bad**: Additional form-validation/test complexity.
**Neutral**: No API or DB schema changes.
