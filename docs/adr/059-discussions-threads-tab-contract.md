# ADR 059 — Discussions Threads Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.5 defines the Discussions Threads tab behavior so users can browse discussion topics with spoiler awareness and clear group/media context.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.5**.

## Decision
1. Threads tab uses existing authenticated discussions listing endpoint(s), optionally scoped by media/group context.
2. State includes `items`, `isLoading`, `error`, pagination state, and optional filters (media, spoiler, recency).
3. Thread cards include title/body preview, author, media context, reply count, recency, and spoiler indicator.
4. Loading/empty/error states use `AppEmptyState` with retry behavior.
5. Thread cards navigate to thread detail route.
6. Responsive behavior preserves spoiler labeling and interaction clarity across xs/sm/md+.
7. Tests cover loading/empty/error/success states, filter behavior, pagination/retry, spoiler badge rendering, and navigation.

## Consequences
**Good**: Better social conversation discovery with safer spoiler signaling.
**Bad**: More conditional rendering complexity (spoiler/media context badges).
**Neutral**: No API or DB schema changes.
