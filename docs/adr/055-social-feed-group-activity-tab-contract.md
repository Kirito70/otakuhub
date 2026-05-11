# ADR 055 — Social Feed Group Activity Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.1 defines the Social Feed Group Activity tab behavior so users can follow friends’ tracking events in shared-group context with spoiler-safe, filterable activity cards.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.1**.

## Decision
1. Group Activity tab uses existing authenticated social feed endpoint contract(s) scoped to shared group visibility.
2. State includes `items`, `isLoading`, `error`, pagination state, and optional filter state (event type/group).
3. Activity cards emphasize actor, media, event type, delta context (status/progress/score), and recency.
4. Loading/empty/error states use shared primitives (`AppEmptyState`) with retry behavior.
5. Cards/actions navigate to relevant media/profile/detail routes when applicable.
6. Responsive behavior preserves readability and action reachability across xs/sm/md+.
7. Tests cover loading/empty/error/success, filter behavior, pagination, retry, and navigation.

## Consequences
**Good**: Stronger group awareness and social engagement signal.
**Bad**: Higher UI complexity for event rendering variants.
**Neutral**: No API or DB schema changes.
