# ADR 047 — Media Detail Relations Tab Contract
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 17.6 defines the Media Detail Relations tab behavior so users can navigate sequels/prequels/spin-offs and related works from a title without leaving the media detail context.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 17.6**.

## Decision
1. Relations tab uses existing backend media detail relation data contract(s); no direct external API calls.
2. Relations are grouped or labeled by relation type (e.g., sequel, prequel, side story, adaptation).
3. Each relation card exposes key metadata (title, format/type/status where available) and navigates to target media detail.
4. Loading, empty, and error states use shared primitives (`AppEmptyState`) with retry behavior.
5. Relations list/grid remains responsive across xs/sm/md+ with no hover-only critical interactions.
6. Navigation preserves route consistency and avoids broken links for missing/deleted targets.
7. Tests cover loading/empty/error/success rendering, relation-type labeling, and navigation traversal behavior.

## Consequences
**Good**: Better franchise traversal and content discovery from within detail pages.
**Bad**: Additional relation-type grouping/labeling logic in UI.
**Neutral**: No API or DB schema changes.
