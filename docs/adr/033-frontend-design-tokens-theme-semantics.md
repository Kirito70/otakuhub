# ADR 033 — Frontend Design Tokens and Theme Semantics (Quasar-native)
**Status**: Proposed
**Date**: 2026-05-11

## Context
Phase 15.1 requires a consistent design token system for light/dark themes so all frontend pages use one visual language. Current UI behavior is functionally stable (Phase 14 complete), but visual semantics are still component-local and inconsistent across screens.

OtakuHub is a small private-group app, so we prioritize maintainable consistency over high-complexity theming systems. We also need a structure that supports upcoming Phase 15 primitives (`AppCard`, `AppBadge`, `AppToolbar`, `AppEmptyState`) without rework.

## Project Status check
Refer to `PROJECT-STATUS.md` before and after this decision.
Current target is **Phase 15.1**.

## Decision
Adopt a semantic token layer on top of Quasar palette variables and runtime dark mode:

1. **Semantic token groups**
   - `surface`: page, card, elevated
   - `text`: primary, secondary, muted, inverse
   - `border`: default, strong, subtle
   - `state`: primary, success, warning, destructive, info
   - `focus`: ring/default focus color

2. **Token source of truth**
   - Define token mappings in frontend theme/composable layer (Phase 7.8 foundation) and SCSS variables.
   - Keep Quasar brand colors as low-level primitives; consume only semantic aliases in app components.

3. **Light/dark parity rule**
   - Every semantic token must have both light and dark values.
   - No component may hardcode literal hex values except within token definition files.

4. **Component contract for upcoming Phase 15.3 primitives**
   - Primitives expose semantic variants (e.g., `tone="muted|primary|destructive"`) rather than raw color props.
   - Primitive internals map variants to semantic tokens.

5. **Accessibility baseline**
   - Text tokens must meet practical contrast expectations for dashboard reading.
   - Destructive and warning states require non-color cues where relevant (icon/label pairing).

## Consequences
**Good**:
- Reduces visual drift and ad-hoc styling across pages.
- Makes light/dark behavior predictable for all upcoming frontend phases.
- Keeps implementation simple and aligned with Quasar-native primitives.

**Bad**:
- Requires refactors of existing component styles to replace direct colors.
- Adds initial design governance overhead (token naming + usage rules).

**Neutral**:
- No backend/API/database impact.
- No changes to auth, sync pipeline, or external API integrations.
