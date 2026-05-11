# ADR 046 — Media Detail Episodes/Chapters Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 17.5 defines the Media Detail Episodes/Chapters tab behavior so users can browse installment lists and perform progress-related actions with clear sorting and fallback states.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 17.5**.

## Decision
1. Episodes/chapters tab uses existing backend media detail/related release data contracts and existing list progress update endpoints.
2. Tab supports sort controls (e.g., ascending/descending by episode/chapter number or release order).
3. Render release rows/cards with installment metadata and clear progress affordances where applicable.
4. Loading, empty, and error states use shared state primitives with retry behavior.
5. Progress actions (where enabled) must route through authenticated list update flows and reflect optimistic/loading/error states clearly.
6. Responsive behavior preserves action discoverability on xs/sm/md+ with no hover-only critical interactions.
7. Tests cover loading/empty/error/success render, sort toggling behavior, progress action state transitions, and retry behavior.

## Consequences
**Good**: Better ongoing tracking flow directly from media detail context.
**Bad**: Additional state complexity for sort + action-in-row behavior.
**Neutral**: No API or DB schema changes.
