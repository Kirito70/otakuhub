# ADR 090 — Ditch Quasar, Adopt shadcn-vue + Tailwind CSS

**Status**: Accepted
**Date**: 2026-06-09

## Context

OtakuHub's frontend has been built on Quasar 2.x (Vue 3) since Phase 1. As the project evolved through Phases 26–28 (streaming UI components), we reached a breaking point:

### What we learned building Phase 26–28

| Observation | Impact |
|---|---|
| Every Quasar component required heavy SCSS overrides to look non-Material | ~40% of CSS was Quasar reset/override |
| `QCard`, `QList`, `QItem`, `QBtn` carry Material Design semantics (ripple, elevation, shape) that fight the dark streaming aesthetic | Developer spent more time fighting framework defaults than building features |
| Quasar's `$q` global object is unavoidable for dark mode, screen breakpoints, and platform detection | Tight coupling to `$q` in every layout file |
| Quasar CLI wraps Vite config — hard to add Tailwind, custom PostCSS plugins, or unconventional build steps | Fighting the framework's build opinion |
| Cross-platform (Electron, Capacitor) via Quasar CLI is convenient but unused — we only target web + Electron | Paying for Capacitor/Android/iOS complexity we don't need |
| Quasar's QForm/QInput pattern is form-oriented, not content-oriented | Auth/setup forms work fine, but media/episode/player components are all custom anyway |

### The real cost of keeping Quasar

1. **Bundle size**: Quasar core + extras adds ~350KB gzipped, of which we use <20% (routing, dark mode, QBtn, QInput, QLayout — rest is dead code)
2. **CSS maintenance**: 5 custom SCSS files overriding Material defaults
3. **Developer velocity**: Every new component requires checking "does the Q* version do what I want, or do I build custom?"
4. **Tailwind incompatibility**: Quasar's BEM-generated class names clash with Tailwind utility philosophy
5. **Skill file overhead**: `quasar-dev` agent skill is ~50% Quasar-specific trivia that doesn't apply to pure Vue 3

### The opportunity

- **shadcn-vue** gives us copy-pasteable, accessible, unstyled primitives (dialog, dropdown, sheet, button, badge, card, tabs, popover, tooltip, input) that are designed to be styled with Tailwind
- **Tailwind CSS** eliminates the override cascade — one utility class system for all styling
- **aniwaves.ru** is the visual target: dark bg (`#0a0a0a`), purple/cyan accents, content-first layout, clean episode lists, hero banners
- All streaming components (AnimeCard, HeroBanner, EpisodeList, VideoPlayer, TrendingCarousel) are already pure Vue 3 + SCSS — no Quasar dependency
- Auth/setup forms, layouts, and page shells are the only Quasar-dependent parts

## Decision

### 1. Remove Quasar entirely

- Delete `quasar.config.ts`
- Remove `@quasar/app-vite`, `@quasar/extras`, `quasar` from `package.json`
- Replace Quasar CLI with plain Vite + `@vitejs/plugin-vue`
- Rip out `src-capacitor/` and `src-electron/` (Electron will be handled differently — see below)

### 2. Adopt Vite + Tailwind CSS v4 + shadcn-vue

**Build stack**:
- `vite` + `@vitejs/plugin-vue` (replacing `@quasar/app-vite`)
- `tailwindcss` v4 with `@tailwindcss/vite` plugin
- `shadcn-vue` for accessible primitives (no more building modals, dropdowns, toggles from scratch)
- `vue-router` (keep as-is — no change)
- `pinia` + `pinia-plugin-persistedstate` (keep as-is — no change)
- `axios` (keep as-is — no change)
- `vitest` + `jsdom` + `@vue/test-utils` (keep as-is — no change)
- `zod` (keep for runtime validation)

**shadcn-vue components we'll use**:
- `Button` (replaces QBtn)
- `Card` (replaces QCard)
- `Badge` (replaces our hand-rolled AppBadge)
- `Input` (replaces QInput)
- `Select` (replaces QSelect)
- `Tabs` (replaces QTab)
- `Dialog` (replaces QDialog)
- `Sheet` (replaces QDrawer for mobile)
- `DropdownMenu` (replaces QMenu)
- `Tooltip` (replaces QTooltip)
- `Avatar` (replaces QAvatar)
- `Separator` (replaces QSeparator)
- `Skeleton` (for loading states)

### 3. Electron: use electron-vite instead of Quasar Electron

Replace `@quasar/app-vite`'s Electron integration with `electron-vite` for a cleaner, Tailwind-compatible Electron setup.

### 4. Simplify platform targets

Remove Capacitor (Android/iOS) — OtakuHub is a private friend-group tool. Web + Electron (Windows/Linux) is sufficient. If mobile is needed later, add it deliberately with a proper native wrapper.

### 5. Keep (no migration needed)

| What | Why |
|---|---|
| Vue 3 + TS (unchanged) | Core framework — no migration |
| vue-router | Routes, guards, lazy loading — all unchanged |
| Pinia stores | Auth, tracking, media, social, notifications — all work as-is |
| axios + interceptors | Boot setup, token attach, 401 refresh — no Quasar dependency |
| Vitest + jsdom + vue-test-utils | Test runner and framework — no Quasar dependency |
| All custom streaming components | AnimeCard, HeroBanner, EpisodeList, VideoPlayer, TrendingCarousel, etc. are pure Vue 3 + SCSS |
| All composables | useAuth, useMediaSearch, useMediaDetail, usePlayerListener — no Quasar dependency |
| All TypeScript types | media.ts, tracking.ts, social.ts, auth.ts, api.ts — no Quasar dependency |

### 6. Migrate (replace Quasar with shadcn-vue + Tailwind)

| Current (Quasar) | New (shadcn-vue + Tailwind) | Effort |
|---|---|---|
| QLayout + QDrawer + QFooter | Custom `<AppShell>` using Tailwind grid/flex | Medium |
| QDark toggle (`$q.dark.set`) | Tailwind `dark:` class strategy | Low |
| QForm + form rules | Vue form + zod validation | Medium |
| QInput with `lazy-rules` | shadcn Input + zod schema | Low |
| QBtn | shadcn Button (`<Button>`) | Low |
| QCard | shadcn Card (`<Card>`) | Low |
| QTab/QTabs | shadcn Tabs (`<Tabs>`) | Low |
| QDialog/QDrawer | shadcn Dialog/Sheet | Medium |
| QCircularProgress (ScoreRing) | Already custom — keep | None |
| QBadge | shadcn Badge | Low |
| QSeparator | `<Separator>` | Low |
| QAvatar | shadcn Avatar | Low |
| QTooltip | shadcn Tooltip | Low |
| QSelect | shadcn Select | Low |
| QSkeleton | shadcn Skeleton | Low |
| Quasar breakpoints (`$q.screen`) | Tailwind `sm:/md:/lg:` | Medium |
| Electron window mgmt | `electron-vite` instead of Quasar Electron | Medium |
| Capacitor mobile | **Drop** — not needed | None |

### 7. SCSS → Tailwind migration strategy

- Keep `tokens.scss` as Tailwind CSS custom properties (or migrate to Tailwind v4's `@theme` directive)
- Replace all SCSS `@mixin` usage with Tailwind `@apply` or utility classes
- `HeroBanner`, `AnimeCard`, etc. gradient overlays → Tailwind `bg-gradient-to-t`
- Responsive breakpoints → Tailwind `sm:`, `md:`, `lg:`

## Consequences

**Good**:
- Bundle reduced by ~300–400KB (removing Quasar + Capacitor)
- CSS maintenance drops from 5+ override files to 1 Tailwind config
- Developer velocity increases — no fighting framework defaults
- Tailwind utility classes eliminate context-switching between HTML and CSS
- shadcn-vue primitives are accessible by default (Radix-based)
- Build is simpler: plain Vite, no Quasar CLI wrapper
- Electron via `electron-vite` is cleaner and fully Tailwind-compatible

**Bad**:
- ~15 page/components need rewiring from Quasar to shadcn-vue
- Layout shell (MainLayout) needs a full rewrite
- Auth/setup forms need re-implementation with shadcn Input + zod
- Existing SCSS in streaming components (`tokens.scss`) needs Tailwind migration
- ~187 Quasar-specific SCSS tests may need selector updates
- Pinia persisted state config needs to change (remove Quasar `$q` references)

**Neutral**:
- All routing, state, HTTP, and composables remain unchanged (~80% of frontend code is untouched)
- The streaming components (AnimeCard, HeroBanner, etc.) already use pure Vue 3 — only their SCSS needs Tailwind conversion
- Test infrastructure (Vitest + vue-test-utils) is unchanged
- Build commands change from `quasar dev` to `vite dev` and `quasar build` to `vite build`

## Migration Phases

### Phase M1 — Foundation (new branch from dev)
- Initialize new Vite + Tailwind v4 + shadcn-vue project
- Copy over: `src/` (with Quasar imports removed), `types/`, `stores/`, `composables/`, `router/`
- Create `tailwind.config.css` with design tokens from `tokens.scss`
- Remove: `quasar.config.ts`, `src-capacitor/`, `src-electron/` (temporarily)
- Verify: `vite dev` launches, Vue app mounts, router works
- Add electron-vite for Electron target

### Phase M2 — Layout & Shell
- Rewrite MainLayout as `<AppShell>` using Tailwind grid
- Implement responsive sidebar + bottom nav (pure Tailwind, no Quasar)
- Wire up dark mode via Tailwind `dark:` class strategy
- Migrate auth guards, setup guards, route redirects

### Phase M3 — shadcn-vue Component Migration
- Install shadcn-vue primitives one by one
- Replace QForm/QInput with shadcn Input + zod validation in auth/setup forms
- Replace QBtn, QCard, QBadge, QDialog, QSheet, QSelect, QAvatar, QTooltip, QSeparator, QSkeleton
- Remove all Quasar imports and `$q` references

### Phase M4 — SCSS → Tailwind Conversion
- Convert `tokens.scss` to Tailwind theme variables
- Convert streaming component SCSS to Tailwind utilities
- Remove leftover SCSS files
- Verify all 399+ tests pass

### Phase M5 — Verification
- `vitest run` — all tests pass
- `vite build` — production build succeeds
- Electron build works
- Visual QA against aniwaves.ru reference
- Remove dead dependencies from package.json

## Files to Change

### Delete
- `quasar.config.ts`
- `src-capacitor/` (entire directory)
- `src-electron/` (will recreate with electron-vite)
- `.quasar/`
- `yarn.lock` (if switching to npm/pnpm)

### Rewrite
- `frontend/src/layouts/MainLayout.vue` → `AppShell.vue`
- `frontend/src/boot/axios.ts` → `src/plugins/axios.ts`
- `frontend/src/boot/pinia.ts` → `src/plugins/pinia.ts`
- All page files using QForm, QInput, QBtn, QCard, QDialog

### Keep (no changes)
- `frontend/src/stores/` (all Pinia stores)
- `frontend/src/composables/` (all composables)
- `frontend/src/types/` (all TypeScript types)
- `frontend/src/components/player/` (VideoPlayer, PlayerControls, PlayerError)
- `frontend/src/components/anime/` (AnimeCard, AnimeGrid, HeroBanner, EpisodeItem, EpisodeList, ServerSelector, TrendingCarousel, RelatedMediaCarousel)
- `frontend/src/components/home/` (FriendActivityRow, SearchBar, GenrePills)
- `frontend/src/components/shared/` (SectionHeader)
- `frontend/src/router/` (routes, index — unchanged)

### Update
- `package.json` — swap Quasar deps for Vite + Tailwind + shadcn-vue deps
- `tsconfig.json` — may need path alias changes (`src/` aliases)
- `vitest.config.ts` — Vite config reference
- `index.html` — entry point (minor)
- All `.env` files — update build references

## Agent & Skill Updates

| Agent | Current Name | New Name | Skill Change |
|---|---|---|---|
| quasar-dev | `quasar-dev` | `vue-dev` | Remove Quasar API refs, add shadcn-vue + Tailwind |
| flutter-dev | `flutter-dev` | `vue-dev` (merged) | Flutter references → Vue 3 + Tailwind |
| architect | `architect` | Keep | Update frontend stack in architecture docs |
| code-reviewer | `code-reviewer` | Keep | Review for Tailwind class usage, no Quasar imports |

All agents must have their system prompts updated to reference the new stack (Vite + Vue 3 + Tailwind + shadcn-vue) instead of Quasar-specific APIs.
