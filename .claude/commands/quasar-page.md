# Scaffold a New Quasar Page

Given a page name and description, generate the full page scaffold.

## Files to Create

### 1. TypeScript Interface — `src/types/<name>.ts`
All types used by this feature — no `any`.

```typescript
export interface MediaSearchResult {
  id: string
  title: { romaji: string; english: string | null; native: string }
  mediaType: 'anime' | 'manga' | 'manhwa'
  coverImageMedium: string | null
  averageScore: number | null
  status: string
}

export interface PaginatedResponse<T> {
  items: T[]
  nextCursor: string | null
  total: number
}
```

### 2. Pinia Store — `src/stores/<name>.ts`
Setup syntax. Every async action has `isLoading`, `error`, `data`.

### 3. Page Component — `src/pages/<Name>Page.vue`
```vue
<template>
  <q-page padding>
    <!-- Loading -->
    <div v-if="store.isLoading" class="flex flex-center" style="min-height: 300px">
      <q-spinner size="48px" color="primary" />
    </div>
    <!-- Error -->
    <q-banner v-else-if="store.error" class="bg-negative text-white rounded-borders">
      {{ store.error }}
      <template #action>
        <q-btn flat color="white" label="Retry" @click="store.fetchData()" />
      </template>
    </q-banner>
    <!-- Content -->
    <template v-else>
      <!-- page content here -->
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useMyStore } from 'src/stores/myStore'

const store = useMyStore()
onMounted(() => { void store.fetchData() })
</script>
```

### 4. Register Route — `src/router/routes.ts`
Add named route to the appropriate layout's children array.

### 5. Component Test — `src/pages/__tests__/<Name>Page.test.ts`
```typescript
import { installQuasarPlugin } from '@quasar/quasar-app-extension-testing-unit-vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { describe, it, expect } from 'vitest'
import MyPage from '../MyPage.vue'

installQuasarPlugin()

describe('MyPage', () => {
  it('shows spinner while loading', () => {
    const wrapper = mount(MyPage, {
      global: {
        plugins: [createTestingPinia({ initialState: { myStore: { isLoading: true } } })]
      }
    })
    expect(wrapper.find('.q-spinner').exists()).toBe(true)
  })

  it('shows error banner on error', () => {
    const wrapper = mount(MyPage, {
      global: {
        plugins: [createTestingPinia({ initialState: { myStore: { error: 'Network error' } } })]
      }
    })
    expect(wrapper.find('.q-banner').exists()).toBe(true)
  })
})
```

## After Generating All Files
```bash
vue-tsc --noEmit
npx eslint src/pages/<name>/ src/stores/<name>.ts
quasar build
```
Zero errors required before marking done.
