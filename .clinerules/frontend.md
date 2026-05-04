---
paths:
  - "frontend/**"
---
# Frontend Rules (Quasar / Vue 3 / TypeScript)

## Component Rules
- ALWAYS use `<script setup lang="ts">` — never Options API or `defineComponent`
- ALWAYS type component props with `defineProps<{...}>()`
- ALWAYS type emits with `defineEmits<{...}>()`
- NEVER use `any` — write a proper interface or use `unknown`
- Import types with `import type { Foo }` — not `import { Foo }` for type-only imports

## Pinia Store Pattern
```typescript
// src/stores/tracking.ts
export const useTrackingStore = defineStore('tracking', () => {
  const entries = ref<ListEntry[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchUserList() {
    isLoading.value = true
    error.value = null
    try {
      const { data } = await api.get<ListEntry[]>('/api/v1/lists/me')
      entries.value = data
    } catch (e) {
      error.value = getErrorMessage(e)
    } finally {
      isLoading.value = false
    }
  }

  return { entries, isLoading, error, fetchUserList }
})
```

## Composable Pattern (for reusable logic)
```typescript
// src/composables/useMediaSearch.ts
export function useMediaSearch() {
  const results = ref<MediaSearchResult[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const search = useDebounceFn(async (query: string) => {
    if (!query.trim()) { results.value = []; return }
    isLoading.value = true
    try {
      const { data } = await api.get('/api/v1/media/search', { params: { q: query } })
      results.value = data.items
    } catch (e) {
      error.value = getErrorMessage(e)
    } finally {
      isLoading.value = false
    }
  }, 300)

  return { results, isLoading, error, search }
}
```

## Responsive Layout
```vue
<template>
  <q-page padding>
    <!-- Mobile: 1 col, Tablet: 2 cols, Desktop: 4 cols -->
    <div class="row q-col-gutter-md">
      <div
        v-for="item in items"
        :key="item.id"
        class="col-12 col-sm-6 col-md-3"
      >
        <AnimeCard :anime="item" />
      </div>
    </div>
  </q-page>
</template>
```

## API Calls — Always Via Axios Boot
```typescript
// CORRECT — use the configured axios instance
import { api } from 'src/boot/axios'
const { data } = await api.get('/api/v1/media/search')

// WRONG — never use fetch() or import axios directly
const res = await fetch('http://...')
import axios from 'axios'
```

## Never
- Never call AniList, MangaDex, or Jikan directly from frontend code
- Never use `localStorage` directly — use Pinia with pinia-plugin-persistedstate
- Never use `$router.push({ path: '...' })` with raw strings — use named routes
- Never use `v-for` on lists > 100 items without `QVirtualScroll`
- Never use `<img>` for remote images — use `<q-img>` with error slot
