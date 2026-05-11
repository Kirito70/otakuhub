# OtakuHub — Quasar Frontend Architecture

## Overview
Single Quasar (Vue 3 + TypeScript) codebase targeting 5 platforms:
- **Web**: SPA or PWA via `quasar build`
- **Windows + Linux**: Electron via `quasar build -m electron`
- **Android + iOS**: Capacitor via `quasar build -m capacitor -T android/ios`

## Project Structure
```
frontend/
├── src/
│   ├── assets/                  ← static assets (logo, illustrations)
│   ├── boot/
│   │   ├── axios.ts             ← Axios instance + auth interceptor
│   │   └── pinia.ts             ← pinia-plugin-persistedstate setup
│   ├── components/
│   │   ├── media/               ← MediaCard.vue, MediaBanner.vue
│   │   ├── tracking/            ← ProgressWidget.vue, ScoreWidget.vue
│   │   ├── social/              ← ActivityFeedItem.vue, RecommendCard.vue
│   │   └── shared/              ← BaseEmptyState.vue, BaseErrorBanner.vue
│   ├── composables/
│   │   ├── useAuth.ts
│   │   ├── useMediaSearch.ts
│   │   └── useInfiniteScroll.ts
│   ├── css/
│   │   ├── app.scss             ← global custom styles (minimal)
│   │   └── quasar.variables.scss ← brand colour overrides
│   ├── layouts/
│   │   ├── MainLayout.vue       ← authenticated shell (nav, sidebar)
│   │   └── AuthLayout.vue       ← login/register (no nav)
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── LoginPage.vue
│   │   │   └── RegisterPage.vue
│   │   ├── discover/
│   │   │   └── DiscoverPage.vue
│   │   ├── media/
│   │   │   └── MediaDetailPage.vue
│   │   ├── tracking/
│   │   │   ├── MyListPage.vue
│   │   │   ├── AiringCalendarPage.vue
│   │   │   └── ImportListPage.vue
│   │   ├── social/
│   │   │   ├── FeedPage.vue
│   │   │   ├── RecommendationsPage.vue
│   │   │   └── DiscussionPage.vue
│   │   ├── watchparty/
│   │   │   └── WatchPartyPage.vue
│   │   ├── notifications/
│   │   │   └── NotificationsPage.vue
│   │   └── profile/
│   │       └── ProfilePage.vue
│   ├── router/
│   │   ├── routes.ts            ← ALL named routes defined here
│   │   └── index.ts             ← router factory + auth guard
│   ├── stores/
│   │   ├── auth.ts              ← tokens, user, login/logout (persisted)
│   │   ├── media.ts             ← search results, detail cache
│   │   ├── tracking.ts          ← user list, progress updates
│   │   ├── social.ts            ← feed, recommendations, discussions
│   │   ├── watchparty.ts
│   │   └── notifications.ts
│   └── types/
│       ├── media.ts
│       ├── tracking.ts
│       ├── social.ts
│       ├── auth.ts
│       └── api.ts               ← shared API types (PaginatedResponse, etc.)
├── src-capacitor/               ← Capacitor native project (auto-generated)
├── src-electron/                ← Electron main process
│   └── electron-main.ts         ← window creation, auto-updater
├── public/                      ← static files (favicon, robots.txt)
├── quasar.config.ts             ← Quasar build config (all targets)
├── tsconfig.json                ← strict TypeScript config
├── .eslintrc.cjs
└── package.json
```

## Key Packages
```json
{
  "dependencies": {
    "quasar": "^2.x",
    "@quasar/extras": "^1.x",
    "vue": "^3.x",
    "vue-router": "^4.x",
    "pinia": "^2.x",
    "pinia-plugin-persistedstate": "^3.x",
    "axios": "^1.x",
    "zod": "^3.x"
  },
  "devDependencies": {
    "@quasar/app-vite": "^1.x",
    "typescript": "^5.x",
    "vue-tsc": "^2.x",
    "vitest": "^1.x",
    "@vue/test-utils": "^2.x",
    "@pinia/testing": "^0.x",
    "@quasar/quasar-app-extension-testing-unit-vitest": "^0.x",
    "eslint": "^8.x",
    "eslint-plugin-vue": "^9.x"
  }
}
```

## State Management (Pinia)

### Store Structure (always setup syntax)
```typescript
export const useTrackingStore = defineStore('tracking', () => {
  // refs = state
  const entries = ref<ListEntry[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // computed = getters
  const watchingCount = computed(() =>
    entries.value.filter(e => e.status === 'watching').length
  )

  // functions = actions
  async function fetchList() { ... }
  async function updateProgress(mediaId: string, progress: number) { ... }

  return { entries, isLoading, error, watchingCount, fetchList, updateProgress }
})
```

### Auth Store (persisted)
The auth store uses `pinia-plugin-persistedstate` to survive page refresh.
On Electron/web: persists to localStorage.
On Capacitor mobile: configure `storage` to use Capacitor Preferences.

## HTTP Client (Axios Boot)

### `src/boot/axios.ts`
```typescript
import axios from 'axios'
import { boot } from 'quasar/wrappers'

const api = axios.create({ baseURL: process.env.API_BASE_URL })

export default boot(({ app }) => {
  // Request interceptor: attach token
  api.interceptors.request.use(config => {
    const auth = useAuthStore()
    if (auth.accessToken) {
      config.headers.Authorization = `Bearer ${auth.accessToken}`
    }
    return config
  })

  // Response interceptor: refresh on 401
  api.interceptors.response.use(
    res => res,
    async err => {
      if (err.response?.status === 401 && !err.config._retry) {
        err.config._retry = true
        const auth = useAuthStore()
        await auth.refreshToken()
        err.config.headers.Authorization = `Bearer ${auth.accessToken}`
        return api(err.config)
      }
      return Promise.reject(err)
    }
  )

  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }
```

## Routing

### Auth Guard
```typescript
// src/router/index.ts
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.accessToken) {
    return { name: 'login' }
  }
  if (to.name === 'login' && auth.accessToken) {
    return { name: 'discover' }
  }
})
```

### Named Routes (all routes in `src/router/routes.ts`)
```typescript
{ path: '/discover',      name: 'discover',      component: () => import('pages/discover/DiscoverPage.vue'),      meta: { requiresAuth: true } },
{ path: '/media/:id',     name: 'media-detail',  component: () => import('pages/media/MediaDetailPage.vue'),      meta: { requiresAuth: true } },
{ path: '/list',          name: 'my-list',        component: () => import('pages/tracking/MyListPage.vue'),        meta: { requiresAuth: true } },
{ path: '/feed',          name: 'feed',           component: () => import('pages/social/FeedPage.vue'),            meta: { requiresAuth: true } },
{ path: '/watchparty',    name: 'watchparty',     component: () => import('pages/watchparty/WatchPartyPage.vue'),  meta: { requiresAuth: true } },
{ path: '/notifications', name: 'notifications',  component: () => import('pages/notifications/NotificationsPage.vue'), meta: { requiresAuth: true } },
```

## Responsive Layout

### Quasar Breakpoints
| Name | Width | QLayout behaviour |
|------|-------|-------------------|
| xs | < 600px | Bottom nav (drawer hidden) |
| sm | 600–1024px | Side nav collapsible |
| md+ | > 1024px | Persistent side nav rail |

### MainLayout.vue pattern
```vue
<q-layout view="lHh Lpr lFf">
  <!-- Desktop: persistent left drawer -->
  <q-drawer v-model="leftDrawerOpen" show-if-above :width="240" bordered>
    <SideNav />
  </q-drawer>

  <q-page-container>
    <router-view />
  </q-page-container>

  <!-- Mobile only: bottom tabs -->
  <q-footer v-if="$q.screen.lt.md">
    <q-tabs :value="activeTab" align="justify">
      <q-tab name="discover" icon="search" @click="go('discover')" />
      <q-tab name="my-list" icon="list" @click="go('my-list')" />
      <q-tab name="feed" icon="people" @click="go('feed')" />
      <q-tab name="notifications" icon="notifications" @click="go('notifications')" />
    </q-tabs>
  </q-footer>
</q-layout>
```

## Platform Build Commands
```bash
# Development
quasar dev                        # web dev server
quasar dev -m electron            # Electron desktop
quasar dev -m capacitor -T android # Android (requires Android Studio)

# Production builds
quasar build                      # web SPA → dist/spa/
quasar build -m pwa               # PWA → dist/pwa/
quasar build -m electron          # Electron → dist/electron/
quasar build -m capacitor -T android  # → src-capacitor/ then Android Studio
quasar build -m capacitor -T ios      # → src-capacitor/ then Xcode
```

## Testing
```bash
# Unit + component tests (Vitest)
npx vitest run

# Specific file
npx vitest run src/pages/__tests__/DiscoverPage.test.ts

# Type check
vue-tsc --noEmit

# Lint
npx eslint src/

# All checks (run before commit)
vue-tsc --noEmit && npx eslint src/ && npx vitest run && quasar build
```

## Environment Variables
```env
# frontend/.env
API_BASE_URL=http://localhost:8000
# frontend/.env.production
API_BASE_URL=https://otakuhub.yourdomain.com
```
Access in code: `process.env.API_BASE_URL` (Quasar injects this via Vite).

## Phase 15.1 Design System Semantics (Architecture Contract)

### Semantic Token Set (light/dark)
- `surface`: `page`, `card`, `elevated`
- `text`: `primary`, `secondary`, `muted`, `inverse`
- `border`: `default`, `strong`, `subtle`
- `state`: `primary`, `success`, `warning`, `destructive`, `info`
- `focus`: `ring`

Rule: app components consume semantic tokens only; raw palette values stay in theme/token definition.

### Layer Boundary Spec (frontend)
- **Router owns**
  - Route resolution, auth/setup guards, and page-level shell selection.
  - Never owns visual token logic.

- **Service/composable owns**
  - Runtime theme mode (`light`/`dark`) and semantic token mapping selection.
  - Exposes token access helpers to components/primitives.
  - Never owns page-specific layout decisions.

- **Repository/API layer owns**
  - Remote data fetching and DTO translation only.
  - No color/theme decisions.

- **Pinia state shape owns**
  - `theme.mode: 'light' | 'dark'`
  - `theme.tokensVersion: string` (optional cache/versioning hook)
  - Derived/computed semantic mappings used by primitives.

### Primitive Contract (Phase 15.3 readiness)
- `AppCard`, `AppBadge`, `AppToolbar`, `AppEmptyState` accept semantic variants (e.g. `tone='muted|primary|destructive'`).
- Variants resolve to semantic tokens internally.
- Components should not pass direct hex or Quasar color names for critical brand/state meaning.

## Phase 15.2 Typography + Spacing Scale (Architecture Contract)

### Typography semantic levels
- Display: `display-lg`, `display-md`
- Headings: `heading-xl`, `heading-lg`, `heading-md`, `heading-sm`
- Body: `body-lg`, `body-md`, `body-sm`
- Utility: `label-md`, `label-sm`, `caption`

Usage rules:
- One dominant page title level per page.
- Descending heading hierarchy by section.
- Metadata/helper content should use body/caption levels only.

### Spacing semantic scale
- Base step: 4px
- Tokens:
  - `space-1`  = 4px
  - `space-2`  = 8px
  - `space-3`  = 12px
  - `space-4`  = 16px
  - `space-5`  = 20px
  - `space-6`  = 24px
  - `space-7`  = 28px
  - `space-8`  = 32px
  - `space-9`  = 40px
  - `space-10` = 48px
  - `space-11` = 56px
  - `space-12` = 64px

Defaults:
- Page horizontal gutter: `space-6` desktop, `space-4` mobile
- Card padding: `space-4` (default), `space-5` (dashboard-dense)
- Section-to-section vertical gap: `space-6`
- Form field stack gap: `space-3`

### Layer boundary alignment
- Router: no typography/spacing decisions.
- Composables/theme services: expose semantic size maps.
- API/repository: no presentation sizing logic.
- Pinia theme state may track scale version (`tokensVersion`) for rollout control.

## Phase 15.3 Shared UI Primitives (Architecture Contract)

### Primitive inventory
- `AppCard`
- `AppBadge`
- `AppToolbar`
- `AppEmptyState`

### Component contracts

#### `AppCard`
- Props:
  - `tone: 'default' | 'muted' | 'elevated' | 'destructive'`
  - `padding: 'sm' | 'md' | 'lg'`
  - `border: 'default' | 'strong' | 'subtle' | 'none'`
- Slots: `header`, `default`, `footer`, `actions`.
- Usage: default content wrapper across dashboard/list/detail screens.

#### `AppBadge`
- Props:
  - `tone: 'primary' | 'success' | 'warning' | 'destructive' | 'info' | 'muted'`
  - `size: 'sm' | 'md'`
- Rule: text-bearing semantic label required (no icon-only badge contract).

#### `AppToolbar`
- Props:
  - `title: string` (required)
  - `subtitle?: string`
  - `dense?: boolean`
- Slots: `leading`, `actions`, `meta`.
- Responsive: stacked content on mobile, single-row composition on md+.

#### `AppEmptyState`
- Props:
  - `mode: 'empty' | 'error' | 'loading_hint'`
  - `title: string`
  - `description?: string`
  - `actionLabel?: string`
  - `onAction?: () => void`
- Rule: actionable mode requires explicit CTA text.

### Token + scale mapping rule
- Primitive variants must resolve through semantic tokens (Phase 15.1) and semantic typography/spacing levels (Phase 15.2).
- No primitive may expose raw hex/color-name props for critical semantics.
- No primitive may expose arbitrary pixel spacing props.

### Layer boundary alignment
- Router owns route/shell decisions only.
- Composable/theme layer owns token and size resolution tables.
- Primitives own visual composition and variant mapping.
- Page components own content orchestration, data wiring, and action handlers.

## Phase 15.4 Dashboard Template (Architecture Contract)

### Template objective
Standardize top-level page composition with a desktop-first, mobile-adaptive dashboard skeleton using Quasar-native layout and shared primitives.

### Standard page composition
1. **Toolbar region**
   - Render `AppToolbar` at top of page.
   - Desktop (`md+`): title/subtitle left, action slot right.
   - Mobile (`lt.md`): stacked title/subtitle/actions.

2. **Content grid region**
   - Use Quasar `row` + `col-*` responsive grid.
   - Desktop default: split primary and secondary content columns.
   - Mobile default: single-column stack.

3. **State region**
   - Loading/empty/error states rendered via `AppEmptyState` only.
   - No custom one-off state block patterns per page.

4. **Card and status region**
   - Use `AppCard` for section containers.
   - Use `AppBadge` for status semantics.

### Zone contract
- `hero`: summary metrics/context.
- `primary`: highest-value user task area.
- `secondary`: supplemental context/actions.
- `state`: fallback UI for loading/empty/error.

### Responsive behavior rules
- No hover-only controls for critical actions.
- Primary CTA always visible on first viewport without hidden menus.
- Gutter/padding/section gaps must follow Phase 15.2 spacing tokens.

### Layer boundary alignment
- Router: route/auth/shell routing only.
- Composable/store: data loading, action handling, and state orchestration.
- Primitive components: visual semantics and structure.
- Page components: map domain data into dashboard zones.

## Phase 15.5 Responsive Validation (Architecture Contract)

### Breakpoint validation matrix
- `xs (<600)`: single-column content stack, visible primary CTA, no horizontal clipping.
- `sm (600–1024)`: compact/two-zone behavior where applicable, critical actions still explicit.
- `md+ (>1024)`: dashboard split layout with persistent desktop navigation affordances.

### Responsive interaction guarantees
- No hover-only dependency for essential actions.
- Drawer/bottom-tab navigation remains reachable after viewport transitions.
- Keyboard focus ring remains visible for interactive elements.

### State and feedback guarantees
- Loading/empty/error states are rendered through `AppEmptyState` at all breakpoints.
- Inline form feedback and disabled-submit behavior remain visible on small screens.

### Verification baseline
- Component/page tests include breakpoint-sensitive behavior where practical.
- Run verification suite before completion:
  - `npx vitest run`
  - `quasar build`
  - Platform mode checks when environment supports them (electron/capacitor).

## Phase 16.1 Login Hardening (Architecture Contract)

### Form behavior contract
- Login form uses shared validation composable rules:
  - required username
  - required password
- Submit disabled when invalid or while request is in-flight.

### Error mapping contract
- `401` -> invalid credentials message (actionable, non-technical).
- `429` -> rate-limit message with retry guidance.
- `5xx`/network -> service unavailable message with retry action.
- Field-level error text reserved for client validation; auth failures shown at form-level.

### State contract
- `isLoading` true during login request.
- Prevent duplicate submit while `isLoading` is true.
- On success, auth store persists tokens then router transitions to authenticated landing.
- On failure, restore interactive controls and preserve user input where safe.

### Testing contract
- Include tests for: empty submit, invalid input, in-flight disable, success redirect, and backend error mapping.

## Phase 16.2 Register Hardening (Architecture Contract)

### Form behavior contract
- Register form uses shared validation rules:
  - required username
  - required valid email
  - required password with strength baseline
  - required confirm-password matching password
- Submit disabled when invalid or while request is in-flight.

### Error mapping contract
- `400` conflict-style errors -> username/email already in use guidance.
- `403` -> setup policy message when public register is disabled post-bootstrap.
- `429` -> rate-limit retry guidance.
- `5xx`/network -> service unavailable/retry message.
- Field-level errors reserved for client validation; backend auth/policy errors shown at form-level.

### State contract
- `isLoading` true during registration request.
- Duplicate submit blocked while `isLoading` is true.
- On success, auth store persistence + authenticated route transition.
- On failure, restore controls and preserve safe user input.

### Testing contract
- Include tests for: empty submit, invalid email, weak password, confirm mismatch, in-flight disable, success redirect, and backend error mapping.

## Phase 16.3 Setup Bootstrap Hardening (Architecture Contract)

### Form behavior contract
- Setup bootstrap form enforces:
  - required username
  - required valid email
  - required password with strength baseline
  - required confirm-password matching password
- Submit disabled when invalid or while request is in-flight.

### One-time flow contract
- Setup route should be accessible only when setup is required.
- Backend `409` response is treated as "already initialized" and transitions user away from setup flow.

### Error mapping contract
- `409` -> setup already completed message + redirect guidance.
- `429` -> rate-limit retry guidance.
- `5xx`/network -> service unavailable/retry message.
- Field-level errors reserved for client validation; backend setup-state errors shown at form-level.

### State contract
- `isLoading` true during bootstrap request.
- Duplicate submit blocked while in-flight.
- On success, transition to authenticated flow (or login fallback policy) with clear user feedback.
- On failure, restore controls and preserve safe user input.

### Testing contract
- Include tests for: empty submit, invalid input, confirm mismatch, in-flight disable, success transition, and 409/429/5xx mapping.

## Phase 16.4 Auth/Setup Test Expansion (Architecture Contract)

### Coverage matrix
- **Login**: empty submit, invalid input, in-flight disable, success redirect, 401/429/5xx mapping.
- **Register**: empty submit, invalid email, weak password, confirm mismatch, in-flight disable, success redirect, 400/403/429/5xx mapping.
- **Setup bootstrap**: empty submit, invalid input, confirm mismatch, in-flight disable, success transition, 409/429/5xx mapping.

### Test design rules
- Prefer user-visible behavior assertions (messages, disabled submit, route transition).
- Keep backend error mapping assertions at form-level banner scope (not field-level unless client validation).
- Maintain route-guard/auth smoke tests alongside form tests to protect deep-link behavior.

### Verification baseline
- Run `npx vitest run` for auth/setup suites before marking completion.
- Maintain compatibility with responsive behavior expectations from Phase 15.5.

## Phase 17.1 Discover — Search Tab (Architecture Contract)

### Data contract
- Uses backend `GET /api/v1/media/search` only.
- No direct external API calls from frontend.

### State contract
- `query: string`
- `results: MediaSearchItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page: number`
- `hasMore: boolean`

### Behavior contract
- Debounced query input.
- New query invalidates stale pending responses.
- Empty query -> guidance state.
- No results -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry action.

### Interaction contract
- Search result card navigates to `media-detail` route.
- Loading skeletons displayed during fetch.
- Responsive parity preserved across xs/sm/md+.

### Testing contract
- Include tests for debounce timing, loading/empty/error/success states, retry, and navigation.

## Phase 17.2 Discover — Trending Tab (Architecture Contract)

### Data contract
- Uses existing backend trending/popular media endpoint(s).
- No direct external API calls from frontend.

### State contract
- `items: MediaListItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore` when pagination is supported

### Behavior contract
- Initial load fetch on tab activation.
- Loading -> skeleton card grid.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Media cards navigate to `media-detail` route.
- Responsive grid behavior preserved across xs/sm/md+.

### Testing contract
- Include tests for loading, empty, error, retry, success render, and navigation.

## Phase 17.3 Discover — New Releases Tab (Architecture Contract)

### Data contract
- Uses existing backend new-release/recent-update media endpoint(s).
- No direct external API calls from frontend.

### State contract
- `items: MediaReleaseItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore` for pagination

### Behavior contract
- Initial load fetch on tab activation.
- Pagination appends additional results in stable chronological order.
- Loading -> skeleton release list/cards.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Release cards navigate to `media-detail` route.
- Episode/chapter release context displayed on each item.
- Responsive list/grid behavior preserved across xs/sm/md+.

### Testing contract
- Include tests for loading, empty, error, retry, pagination append, and navigation.

## Phase 17.4 Media Detail — Overview Tab (Architecture Contract)

### Data contract
- Uses backend `GET /api/v1/media/{id}` for primary media detail data.
- Uses existing list-action endpoints for add/update tracking state.

### State contract
- `media: MediaDetail | null`
- `isLoading: boolean`
- `error: string | null`
- `isSynopsisExpanded: boolean`
- `listActionState` (idle/loading/error/success)

### Behavior contract
- Initial page/tab load fetches media detail.
- Hero metadata includes title, cover/banner, type/format/status, score/popularity when available.
- Synopsis supports expand/collapse behavior for long content.
- Missing/failed states render through `AppEmptyState` with retry action.

### Interaction contract
- Primary CTA supports add/update list behavior and reflects current entry state.
- CTA placement remains prominent on xs/sm/md+.
- Overview preserves semantic card/layout/token rules from Phase 15.

### Testing contract
- Include tests for loading/error/success states, synopsis toggle, primary CTA visibility, and list-action flow behavior.

## Phase 17.5 Media Detail — Episodes/Chapters Tab (Architecture Contract)

### Data contract
- Uses existing backend media detail sub-resources for episodes/chapters.
- Uses existing tracking/list update endpoints for progress actions.

### State contract
- `items: EpisodeItem[] | ChapterItem[]`
- `isLoading: boolean`
- `error: string | null`
- `sortOrder: 'asc' | 'desc'`
- `progressActionState` (idle/loading/error/success)

### Behavior contract
- Initial tab load fetches installment data.
- Sort toggle reorders list deterministically.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Installment entries show episode/chapter context and release metadata when available.
- Progress-related actions route through list-update flow and expose actionable feedback.
- Responsive list behavior preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, sort behavior, progress action flow, and retry.

## Phase 17.6 Media Detail — Relations Tab (Architecture Contract)

### Data contract
- Uses existing backend media relation data associated with media detail.
- No direct external API calls from frontend.

### State contract
- `relations: MediaRelationItem[]`
- `isLoading: boolean`
- `error: string | null`

### Behavior contract
- Initial tab load fetches relation data.
- Relation entries expose relation-type context (sequel/prequel/etc.).
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Relation cards navigate to target `media-detail` route.
- Traversal between related titles must preserve responsive parity across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, relation labeling, and relation-card navigation.

## Phase 18.1 My List — Watching/Reading Tab (Architecture Contract)

### Data contract
- Uses authenticated tracking list endpoint(s) with active-status filtering.
- Uses existing list update endpoint(s) for progress actions.

### State contract
- `items: ListEntryItem[]`
- `isLoading: boolean`
- `error: string | null`
- `entryActionState: Record<entryId, 'idle' | 'loading' | 'error' | 'success'>`

### Behavior contract
- Initial tab load fetches watching/reading entries.
- Default sort favors recently updated entries.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Entries show progress context and quick-update controls.
- Progress actions call existing PATCH list contract and surface inline feedback.
- Responsive list/actions parity preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, quick progress action flow, and retry.

## Phase 18.2 My List — Completed Tab (Architecture Contract)

### Data contract
- Uses authenticated tracking list endpoint(s) filtered to completed statuses.
- Uses existing list update endpoint(s) for score/rewatch actions.

### State contract
- `items: ListEntryItem[]`
- `isLoading: boolean`
- `error: string | null`
- `entryActionState: Record<entryId, 'idle' | 'loading' | 'error' | 'success'>`

### Behavior contract
- Initial tab load fetches completed entries.
- Entries expose completion context (score/completed date/progress snapshot where available).
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Quick actions support score edits and rewatch/reread status transitions via existing PATCH flow.
- Inline feedback surfaces action success/failure without losing list context.
- Responsive parity preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, score action flow, rewatch/reread actions, and retry.

## Phase 18.3 My List — Paused Tab (Architecture Contract)

### Data contract
- Uses authenticated tracking list endpoint(s) filtered to paused status.
- Uses existing list update endpoint(s) for resume/progress actions.

### State contract
- `items: ListEntryItem[]`
- `isLoading: boolean`
- `error: string | null`
- `entryActionState: Record<entryId, 'idle' | 'loading' | 'error' | 'success'>`

### Behavior contract
- Initial tab load fetches paused entries.
- Entries expose pause/resume context (progress and recency metadata).
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Quick actions support resume transitions back to watching/reading.
- Optional progress updates route through existing PATCH list flow.
- Responsive parity preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, resume action flow, and retry.

## Phase 18.4 My List — Dropped Tab (Architecture Contract)

### Data contract
- Uses authenticated tracking list endpoint(s) filtered to dropped status.
- Uses existing list update endpoint(s) for recovery actions.

### State contract
- `items: ListEntryItem[]`
- `isLoading: boolean`
- `error: string | null`
- `entryActionState: Record<entryId, 'idle' | 'loading' | 'error' | 'success'>`

### Behavior contract
- Initial tab load fetches dropped entries.
- Entries expose dropped-context metadata (progress/notes/recency when available).
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Quick actions support recovery transitions to active/backlog statuses.
- Recovery updates route through existing PATCH list flow with inline feedback.
- Responsive parity preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, recovery action flow, and retry.

## Phase 18.5 My List — Plan to Watch/Read Tab (Architecture Contract)

### Data contract
- Uses authenticated tracking list endpoint(s) filtered to plan statuses.
- Uses existing list update endpoint(s) for start/re-prioritize actions.

### State contract
- `items: ListEntryItem[]`
- `isLoading: boolean`
- `error: string | null`
- `entryActionState: Record<entryId, 'idle' | 'loading' | 'error' | 'success'>`

### Behavior contract
- Initial tab load fetches plan/backlog entries.
- Supports backlog prioritization and ordering controls where available.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Quick actions support transitions to active statuses (watching/reading).
- Updates route through existing PATCH list flow with inline feedback.
- Responsive parity preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, prioritization/sort behavior, transition action flow, and retry.

## Phase 18.6 My List — Custom Lists Tab (Architecture Contract)

### Data contract
- Uses authenticated custom-list endpoint(s) for list CRUD and entry management.
- Uses existing custom-list entries replace/update endpoint(s) for ordering and membership changes.

### State contract
- `lists: CustomListItem[]`
- `selectedListId: string | null`
- `entries: CustomListEntryItem[]`
- `isLoading: boolean`
- `error: string | null`
- `listActionState` and `entryActionState` (idle/loading/error/success)

### Behavior contract
- Initial tab load fetches custom lists and selected list entries.
- Supports create/edit/delete list operations.
- Supports add/remove/reorder entries with persisted sort order.
- Empty states (no lists/no entries) use `AppEmptyState(mode='empty')`.
- Failure uses `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Destructive actions require explicit user confirmation.
- Reorder operations provide clear save/success feedback.
- Responsive parity preserved across xs/sm/md+.

### Testing contract
- Include tests for create/edit/delete list flows, entry reorder persistence, loading/empty/error states, and retry.

## Phase 18.7 Airing Calendar Page (Architecture Contract)

### Data contract
- Uses existing backend airing endpoint(s) for scheduled episodes/releases.
- No direct external API calls from frontend.

### State contract
- `items: AiringItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore`
- optional `selectedWindow` (day/week context)

### Behavior contract
- Initial page load fetches airing data.
- Entries grouped by date/time with timezone-safe labels.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Airing entries navigate to `media-detail`.
- Pagination/load-more preserves stable ordering.
- Responsive schedule readability preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, timezone/date-label behavior, pagination, retry, and navigation.

## Phase 19.1 Feed — Group Activity Tab (Architecture Contract)

### Data contract
- Uses authenticated social feed endpoint(s) scoped to shared group activity.
- No direct external API calls from frontend.

### State contract
- `items: FeedActivityItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore`
- optional `filters` (event type/group context)

### Behavior contract
- Initial tab load fetches group activity entries.
- Supports lightweight filtering when available.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Activity cards expose actor/media/event context and relative recency.
- Card actions navigate to relevant routes (media/profile) when applicable.
- Responsive card readability preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, filter behavior, pagination, retry, and navigation.

## Phase 19.5 Discussions — Threads Tab (Architecture Contract)

### Data contract
- Uses authenticated discussions listing endpoint(s).
- No direct external API calls from frontend.

### State contract
- `items: DiscussionThreadItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore`
- optional `filters` (media/spoiler/recency)

### Behavior contract
- Initial tab load fetches discussion threads.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Thread cards expose title/body preview, author/media context, recency, and spoiler markers.
- Thread card actions navigate to thread-detail route.
- Responsive card readability preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, filter behavior, pagination, retry, spoiler labeling, and navigation.

## Phase 19.6 Discussions — Thread Detail Tab (Architecture Contract)

### Data contract
- Uses authenticated discussion detail + replies endpoint(s).
- No direct external API calls from frontend.

### State contract
- `thread: DiscussionThreadDetail | null`
- `replies: DiscussionReplyItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore` for reply pagination where supported
- `replyActionState` (idle/loading/error/success)

### Behavior contract
- Initial tab load fetches thread detail and initial replies.
- Empty replies state uses `AppEmptyState(mode='empty')` while preserving thread context.
- Failure uses `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Thread and replies expose spoiler markers with explicit reveal controls.
- Reply actions (create/post where enabled) use existing discussion reply contracts.
- Responsive readability preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, spoiler reveal behavior, reply flow/pagination, retry, and navigation stability.

## Phase 19.7 Discussions — Create Tab (Architecture Contract)

### Data contract
- Uses authenticated discussion create endpoint(s).
- No direct external API calls from frontend.

### State contract
- `mediaContext` / `groupContext`
- `form: { title, body, hasSpoilers, episodeNumber?, chapterNumber? }`
- `isLoading: boolean`
- `error: string | null`

### Behavior contract
- Form validates required fields before submit.
- Spoiler flag is explicit and user-controlled.
- Submit disabled while invalid or in-flight.
- Success transitions to thread-detail/list context with feedback.
- Failure maps backend errors to actionable form-level messages.

### Interaction contract
- Media/context selection remains visible during authoring.
- Spoiler-marked creation clearly indicated before submit.
- Responsive form readability preserved across xs/sm/md+.

### Testing contract
- Include tests for empty/invalid submit, spoiler toggle behavior, in-flight disable, success transition, and backend error mapping.

## Phase 19.8 Social Page Tests (Architecture Contract)

### Coverage matrix
- **Feed**: group tab + my activity tab (loading/empty/error/success, filters, pagination, retry, navigation).
- **Recommendations**: inbox + sent tabs (loading/empty/error/success, acknowledge/status states, pagination, retry, navigation).
- **Discussions**: threads + thread detail + create tabs (state coverage, spoiler signaling/reveal behavior, pagination/reply flows, create validation + submit lock).

### Test design rules
- Prefer user-visible behavior assertions over implementation details.
- Keep error-state assertions at actionable UI message level.
- Preserve responsive behavior expectations when asserting interaction availability.

### Verification baseline
- Run `npx vitest run` for social suites before marking completion.
- Keep route/auth smoke checks passing for social deep-link flows.

## Phase 19.3 Recommendations — Inbox Tab (Architecture Contract)

### Data contract
- Uses authenticated recommendations inbox endpoint(s).
- No direct external API calls from frontend.

### State contract
- `items: RecommendationItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore`
- `ackActionState: Record<recommendationId, 'idle' | 'loading' | 'error' | 'success'>`

### Behavior contract
- Initial tab load fetches inbox recommendations.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Recommendation cards expose sender/media/message/recency context.
- Acknowledge actions route through existing PATCH acknowledge flow.
- Card actions navigate to relevant routes (media/profile) when applicable.

### Testing contract
- Include tests for loading/empty/error/success states, acknowledge flow, retry, pagination, and navigation.

## Phase 19.4 Recommendations — Sent Tab (Architecture Contract)

### Data contract
- Uses authenticated recommendations endpoint(s) scoped to sent recommendations.
- No direct external API calls from frontend.

### State contract
- `items: RecommendationItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore`
- optional `filters` (acknowledged state)

### Behavior contract
- Initial tab load fetches sent recommendations.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Recommendation cards expose recipient/media/message/acknowledgement context.
- Card actions navigate to relevant routes (media/profile) where applicable.
- Responsive card readability preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, filter behavior, pagination, retry, and navigation.

## Phase 19.2 Feed — My Activity Tab (Architecture Contract)

### Data contract
- Uses authenticated social/activity endpoint(s) scoped to current user activity.
- No direct external API calls from frontend.

### State contract
- `items: FeedActivityItem[]`
- `isLoading: boolean`
- `error: string | null`
- `page/cursor` and `hasMore`
- optional `filters` (event type)

### Behavior contract
- Initial tab load fetches current-user activity entries.
- Supports lightweight event-type filtering where available.
- Empty -> `AppEmptyState(mode='empty')`.
- Failure -> `AppEmptyState(mode='error')` with retry.

### Interaction contract
- Activity cards expose personal event deltas and recency context.
- Card actions navigate to relevant routes (media/list) when applicable.
- Responsive card readability preserved across xs/sm/md+.

### Testing contract
- Include tests for loading/empty/error/success states, filter behavior, pagination, retry, and navigation.
