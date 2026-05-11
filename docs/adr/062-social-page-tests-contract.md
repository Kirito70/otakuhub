# ADR 062 — Social Page Test Coverage Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 19.8 defines required test coverage for Social frontend pages delivered in Phase 19 (feed, recommendations, discussions). This locks in behavior contracts before moving to subsequent feature phases.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 19.8**.

## Decision
1. Maintain a social-page test matrix covering:
   - Feed (group + my activity),
   - Recommendations (inbox + sent),
   - Discussions (threads + thread detail + create).
2. Each page/tab must verify loading/empty/error/success states.
3. Interaction coverage includes filters, pagination/load-more, retry actions, and key route navigation.
4. Discussion coverage includes spoiler signaling/reveal behavior and create-form validation/submit lock.
5. Recommendation coverage includes acknowledge flow and outbound status rendering.
6. Tests should assert user-visible outcomes rather than implementation internals where practical.
7. Verification baseline: run `npx vitest run` for social suites before marking completion.

## Consequences
**Good**: Preserves social UX quality and reduces regressions during future refactors.
**Bad**: Additional test maintenance/runtime cost.
**Neutral**: No API or DB schema changes.
