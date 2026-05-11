# ADR 060 — Discussions Thread Detail Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.6 defines the Discussions Thread Detail tab behavior so users can read full thread context, browse replies, and interact with spoiler-marked content safely.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.6**.

## Decision
1. Thread Detail tab uses existing authenticated discussion detail/replies endpoint contracts.
2. State includes `thread`, `replies`, `isLoading`, `error`, pagination state for replies (if paginated), and reply-action state.
3. UI renders thread header/body metadata plus ordered replies with clear author/recency context.
4. Spoiler-marked thread/reply content uses explicit reveal affordance; hidden-by-default policy for spoiler body where configured.
5. Loading/empty/error states use shared primitives with retry behavior.
6. Reply interactions (where enabled) route through existing reply endpoints and provide inline success/error feedback.
7. Responsive behavior preserves readability and action accessibility across xs/sm/md+.
8. Tests cover loading/empty/error/success rendering, spoiler reveal behavior, reply pagination/actions, retry, and navigation stability.

## Consequences
**Good**: Improves discussion depth and spoiler-safe participation.
**Bad**: Increased state complexity for nested replies and spoiler reveal controls.
**Neutral**: No API or DB schema changes.
