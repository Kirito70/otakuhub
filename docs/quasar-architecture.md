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
