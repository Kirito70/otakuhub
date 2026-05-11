# ADR 045 — Media Detail Overview Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 17.4 defines the Media Detail Overview tab contract so users can quickly understand a title and take primary actions (especially add/update list status) from one stable entry point.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 17.4**.

## Decision
1. Overview tab uses existing backend media detail contract (`GET /api/v1/media/{id}`) and related list-action endpoints already in place.
2. Overview header shows core identity: title variants, cover/banner, media type/format/status, and score/popularity metadata when present.
3. Synopsis section supports collapsed/expanded reading behavior for long descriptions.
4. Primary CTA area includes Add-to-list / Update-list actions with clear current-state reflection.
5. Loading, empty-missing, and error states use shared primitives (`AppCard`, `AppEmptyState`) with retry behavior.
6. Responsive behavior keeps key CTA visible above fold on mobile where feasible.
7. Tests cover loading/error/success rendering, synopsis expand/collapse, CTA visibility, and list-action navigation/dispatch behavior.

## Consequences
**Good**: Clearer first impression and actionability on media pages.
**Bad**: More UI state branches for optional metadata and long synopsis handling.
**Neutral**: No API/DB schema changes.
