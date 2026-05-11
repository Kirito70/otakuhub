# ADR 067 — Watch Party Page Test Coverage Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 20.5 defines required test coverage for Watch Party frontend pages delivered in Phase 20 (upcoming, create, detail, past) to lock behavior before moving to Notifications pages.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 20.5**.

## Decision
1. Maintain watch-party test matrix covering:
   - Upcoming tab,
   - Create tab,
   - Detail tab,
   - Past tab.
2. Every tab must validate loading/empty/error/success state rendering.
3. Interaction coverage includes pagination/retry, navigation, and responsive CTA visibility checks where practical.
4. Create tab coverage includes validation, URL checks, and in-flight submit lock.
5. Detail tab coverage includes RSVP transitions and role-gated actions.
6. Past tab coverage includes status labeling/filter behavior.
7. Verification baseline: run `npx vitest run` for watch-party suites prior to completion.

## Consequences
**Good**: Preserves watch-party flow quality and prevents regressions.
**Bad**: Increased test maintenance and runtime cost.
**Neutral**: No API or DB schema changes.
