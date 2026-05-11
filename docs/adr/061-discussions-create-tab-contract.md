# ADR 061 — Discussions Create Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.7 defines the Discussions Create tab behavior so users can author new threads with clear media context, spoiler signaling, and validation safeguards.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.7**.

## Decision
1. Create tab uses existing authenticated discussion-create endpoint contract(s).
2. Form state includes selected media/context, title/body fields, spoiler flag, `isLoading`, and form-level error state.
3. Validation enforces required fields and basic length constraints before submission.
4. Spoiler toggle is explicit and clearly labeled; default behavior is non-spoiler unless user marks otherwise.
5. Submit locks during in-flight request to prevent duplicates.
6. Success path returns user to thread detail/list context with success feedback.
7. Failure path maps backend validation/policy errors to actionable form-level messages.
8. Loading/empty/error helper states and confirmations follow shared primitive patterns.
9. Tests cover empty/invalid submit, spoiler toggle behavior, in-flight submit lock, success transition, and error mapping.

## Consequences
**Good**: Safer, clearer thread creation flow with spoiler-aware defaults.
**Bad**: More form-state validation paths to maintain.
**Neutral**: No API or DB schema changes.
