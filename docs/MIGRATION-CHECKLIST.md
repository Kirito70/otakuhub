# Frontend Migration Checklist — Quasar → shadcn-vue + Tailwind

> **ADR**: `docs/adr/090-ditch-quasar-shadcn-tailwind.md`
> **Target**: aniwaves.ru visual design
> **Status**: 🟡 Planning — not started

## Phase M1 — Foundation (Vite + Tailwind + shadcn-vue)

### Build Setup
- [ ] Initialize new Vite + Vue 3 + TS project
- [ ] Add `tailwindcss` v4 with `@tailwindcss/vite` plugin
- [ ] Add `shadcn-vue` and initialize (`npx shadcn-vue init`)
- [ ] Add `electron-vite` for Electron target
- [ ] Update `package.json` scripts: `vite dev`, `vite build`, `npm run dev:electron`, `npm run build:electron`
- [ ] Remove Quasar deps: `quasar`, `@quasar/extras`, `@quasar/app-vite`
- [ ] Remove Capacitor deps and `src-capacitor/` directory
- [ ] Update `tsconfig.json` for path aliases (`@/` → `src/`)
- [ ] Update `vite.config.ts` with Tailwind plugin + path aliases
- [ ] Update `vitest.config.ts` for new Vite config
- [ ] Update `index.html` — remove Quasar scripts, update entry point
- [ ] Add `globals.css` with Tailwind directives
- [ ] Configure dark mode via `class` strategy (add `dark` class to `<html>`)

### Keep
- [ ] `src/stores/` — all Pinia stores (auth, tracking, media, social, watchparty, notifications)
- [ ] `src/composables/` — all composables (useAuth, useMediaSearch, useMediaDetail, usePlayerListener, useInfiniteScroll)
- [ ] `src/types/` — all TypeScript types
- [ ] `src/router/` — routes and router index (minor config changes only)
- [ ] `src/components/player/` — VideoPlayer, PlayerControls, PlayerError, ServerSelector
- [ ] `src/components/anime/` — AnimeCard, AnimeGrid, HeroBanner, EpisodeItem, EpisodeList, ServerSelector, TrendingCarousel, RelatedMediaCarousel
- [ ] `src/components/home/` — FriendActivityRow, SearchBar, GenrePills
- [ ] `src/components/shared/` — SectionHeader, ScoreRing

### Verify
- [ ] `vite dev` launches and app mounts
- [ ] Router works (all named routes resolve)
- [ ] Auth guards fire correctly
- [ ] `vite build` succeeds

---

## Phase M2 — Layout & Shell ✅

### AppShell (replaces MainLayout.vue)
- [x] Create `src/components/layout/AppShell.vue`
- [x] Implement desktop sidebar (fixed left, `hidden lg:block`)
- [x] Implement mobile bottom nav (`fixed bottom-0 lg:hidden`)
- [x] Implement top bar with search + notifications + user menu
- [x] Wire up dark mode via Tailwind `dark:` class (remove `$q.dark.set` usage)
- [x] Responsive content area: `lg:ml-60` sidebar offset
- [x] Mobile sidebar drawer with fade overlay + slide transition

### Old file cleanup
- [x] Remove `src/layouts/MainLayout.vue`
- [x] Remove `src/layouts/AuthLayout.vue` (simplify to a single Vue file or inline)

### Router updates
- [x] Update `App.vue` to use new AppShell
- [x] Remove `meta.layout` references if any
- [x] Ensure setup/guest routes still work without auth shell

### Verify
- [ ] Desktop: sidebar visible, responsive at all widths
- [ ] Mobile: bottom nav visible, sidebar hidden
- [ ] Dark mode: bg `#0a0a0a`, text white throughout
- [ ] Navigation works: all routes accessible from sidebar/bottom nav

---

## Phase M3 — shadcn-vue Component Migration

## Quasar → shadcn-vue Replacement Map

### Forms (Login, Register, Setup, Profile Edit, Account Security)
- [ ] `QForm` → `<form>` with zod validation
- [ ] `QInput` → `<Input>` (shadcn)
- [ ] `QBtn` → `<Button variant="...">` (shadcn)
- [ ] `QSelect` → `<Select>` (shadcn)
- [ ] `QToggle` → `<Switch>` or custom checkbox
- [ ] Remove Quasar `lazy-rules` → zod `safeParse`
- [ ] Add form error display: `<p class="text-sm text-red-500">`

### Cards & Display
- [ ] `QCard` → `<Card>` (shadcn)
- [ ] `QCardSection` → `<CardHeader>` / `<CardContent>` / `<CardFooter>`
- [ ] `QSeparator` → `<Separator>`
- [ ] `QBadge` → `<Badge>`
- [ ] `QAvatar` → `<Avatar>` + `<AvatarImage>` + `<AvatarFallback>`
- [ ] `QImg` → native `<img>` with Tailwind classes
- [ ] `QSpinner` → `<Skeleton>`
- [ ] `QCircularProgress` → already custom (ScoreRing) — keep as-is

### Navigation & Menus
- [ ] `QTabs` + `QTab` → `<Tabs>` + `<TabsList>` + `<TabsTrigger>` + `<TabsContent>`
- [ ] `QDrawer` → `<Sheet>` (mobile sidebar)
- [ ] `QMenu` → `<DropdownMenu>`
- [ ] `QTooltip` → `<Tooltip>`

### Dialogs & Overlays
- [ ] `QDialog` → `<Dialog>` + `<DialogTrigger>` + `<DialogContent>`
- [ ] `QBanner` → custom with Tailwind

### Notifications/Toast
- [ ] `$q.notify()` → sonner/vue-sonner `<Toaster>` + `toast()`
- [ ] Remove `$q.loading.show()` / `$q.loading.hide()` → custom component or `v-if`

### File-by-file migration list
**Phase 26 components** (already pure Vue 3 — no migration needed):
- [ ] AnimeCard.vue — ✅ No Quasar imports
- [ ] AnimeGrid.vue — ✅ No Quasar imports
- [ ] HeroBanner.vue — ✅ No Quasar imports
- [ ] EpisodeItem.vue — ✅ No Quasar imports
- [ ] EpisodeList.vue — ✅ No Quasar imports
- [ ] ServerSelector.vue — ✅ No Quasar imports
- [ ] VideoPlayer.vue — ✅ No Quasar imports
- [ ] PlayerControls.vue — ✅ No Quasar imports
- [ ] PlayerError.vue — ✅ No Quasar imports
- [ ] TrendingCarousel.vue — ✅ No Quasar imports
- [ ] ScoreRing.vue — ✅ No Quasar imports

**Files that still use Quasar (need migration)**:
- [ ] `src/pages/auth/LoginPage.vue` — QForm, QInput, QBtn
- [ ] `src/pages/auth/RegisterPage.vue` — QForm, QInput, QBtn
- [ ] `src/pages/auth/SetupPage.vue` — QForm, QInput, QBtn
- [ ] `src/pages/discover/DiscoverPage.vue` — QTabs, QTab
- [ ] `src/pages/media/MediaDetailPage.vue` — QBtn, QTab (already partially custom)
- [ ] `src/pages/tracking/MyListPage.vue` — QTab, QCard
- [ ] `src/pages/tracking/AiringCalendarPage.vue` — QCard
- [ ] `src/pages/tracking/ImportListPage.vue` — QForm, QInput, QBtn, QCard
- [ ] `src/pages/social/FeedPage.vue` — QTab, QCard
- [ ] `src/pages/social/RecommendationsPage.vue` — QCard
- [ ] `src/pages/social/DiscussionPage.vue` — QCard
- [ ] `src/pages/watchparty/WatchPartyPage.vue` — QForm, QInput, QBtn, QCard
- [ ] `src/pages/notifications/NotificationsPage.vue` — QCard
- [ ] `src/pages/profile/ProfilePage.vue` — QForm, QInput, QBtn
- [ ] `src/components/shared/AddToListSheet.vue` — QBtn, QSelect
- [ ] `src/components/shared/AppPageState.vue` — QSpinner
- [ ] `src/components/shared/BaseEmptyState.vue` — QBtn
- [ ] `src/components/shared/BaseErrorBanner.vue` — QBtn

### Verify
- [ ] No `import.*from.*quasar` in any file
- [ ] No `$q.` access in any file
- [ ] No `.quasar/` or `quasar.config.ts` references
- [ ] All forms validate and submit correctly
- [ ] All tests pass

---

## Phase B1 — Backend Migration / Auto-Migration Fix

### Database auto-migration on startup
- [x] `connect_db()` enables `pg_trgm`, `unaccent`, `btree_gin` extensions before table creation
- [x] `SQLModel.metadata.create_all` creates tables from model definitions (idempotent via `checkfirst=True`)
- [x] `alembic_version` table auto-stamped to head after `create_all` prevents DuplicateTableError
- [x] Alembic `env.py` also enables PostgreSQL extensions before running migrations

### Migration file fixes
- [x] `001_initial_tables.py`: `ondelete="SET_NULL"` → `ondelete="SET NULL"` (4 FK columns)

## Phase M4 — SCSS → Tailwind Conversion

### Token Migration
- [ ] Copy `tokens.scss` values into Tailwind `@theme` directive in `globals.css`
- [ ] Colors: `--bg-primary`, `--accent` etc. → Tailwind theme colors
- [ ] Typography: define font-size/font-weight in Tailwind
- [ ] Spacing: verify Tailwind spacing (4px base) matches existing

### SCSS file migration
- [ ] `src/css/app.scss` → remove, use `globals.css`
- [ ] `src/css/quasar.variables.scss` → remove (Quasar-specific)
- [ ] `src/css/tokens.scss` → migrate to Tailwind theme
- [ ] All component `<style scoped>` with SCSS → Tailwind utility classes
- [ ] Remove `lang="scss"` from all `<style>` blocks (convert to Tailwind)

### SCSS Pattern Translation
| SCSS Pattern | Tailwind Equivalent |
|---|---|
| `@mixin text-ellipsis` | `truncate` |
| `@include respond-to('md')` | `md:` prefix |
| `$bg-primary` | `bg-[#0a0a0a]` or `bg-primary` |
| `@media (max-width: 768px)` | `max-md:` prefix |
| `background: linear-gradient(...)` | `bg-gradient-to-t from-black/50` |
| `border-radius: 8px` | `rounded-lg` |
| `box-shadow: 0 4px...` | `shadow-lg` |
| `padding: 16px` | `p-4` |

### Verify
- [ ] Visual comparison against aniwaves.ru for: home page, media detail, player
- [ ] Dark theme consistent across all pages
- [ ] Animations/transitions work (hover overlays, carousel)
- [ ] No SCSS files remain (except maybe third-party)

---

## Phase M5 — Verification

### Build Tests
- [ ] `vue-tsc --noEmit` — type check passes
- [ ] `npx eslint src/` — lint passes
- [ ] `npx vitest run` — all 399+ tests pass
- [ ] `vite build` — production build succeeds

### Platform Checks
- [ ] Web SPA: `vite build` → `dist/` serves correctly
- [ ] Electron: `npm run build:electron` builds and launches

### Visual QA
- [ ] Home page: hero carousel, trending, new releases, continue watching
- [ ] Media detail: hero banner, tabs (episodes/info/related), player overlay
- [ ] Discover: search, trending, new releases tabs
- [ ] My List: status tabs, progress updates, custom lists
- [ ] Auth: login, register, setup forms
- [ ] Social: feed, recommendations, discussions
- [ ] Watch Party: create, detail, RSVP
- [ ] Notifications: inbox, preferences
- [ ] Profile: overview, edit, security

### Cleanup
- [ ] Remove `quasar.config.ts`
- [ ] Remove `src-capacitor/`
- [ ] Remove old Electron config (will be replaced by electron-vite)
- [ ] Remove `yarn.lock` (or replace with `package-lock.json`/`pnpm-lock.yaml`)
- [ ] Remove unused Quasar/Capacitor deps from `package.json`
- [ ] Run `npm prune`
- [ ] Verify no Quasar files remain in `node_modules/` (check bundle)

### Merge
- [ ] Final `git add -A && git commit -m "feat: Quasar → shadcn-vue + Tailwind migration"`
- [ ] Push to `dev`
- [ ] Delete old `docs/quasar-architecture.md` (now `docs/frontend-architecture.md`)
