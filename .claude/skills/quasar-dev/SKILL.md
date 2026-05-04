---
name: quasar-dev
description: Build a Quasar/Vue 3 feature: TypeScript types, Pinia store, page component, shared components, route registration, and Vitest component test.
---

# Quasar Feature Development Skill

## Execution Order
Always build in this sequence:

### Step 1 — Types (`src/types/<name>.ts`)
Define all interfaces for this feature. No `any`. Use `string | null` not `string?` for nullable fields.

### Step 2 — Pinia Store (`src/stores/<name>.ts`)
Setup store syntax. Pattern for every async action:
```typescript
const isLoading = ref(false)
const error = ref<string | null>(null)

async function fetchSomething() {
  isLoading.value = true
  error.value = null
  try {
    const { data } = await api.get<ResponseType>('/api/v1/...')
    // update state
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error'
  } finally {
    isLoading.value = false
  }
}
```

### Step 3 — Shared Components (if needed, `src/components/<Name>Card.vue` etc.)
- Props typed with `defineProps<{...}>()`
- Emits typed with `defineEmits<{...}>()`
- Use Quasar components: `QCard`, `QImg`, `QBadge`, `QChip`, `QRating`
- Responsive image: `<q-img :src="url" :ratio="2/3" style="border-radius: 8px">`

### Step 4 — Page (`src/pages/<Name>Page.vue`)
- Always: loading state → error state → content
- Responsive grid: `class="col-12 col-sm-6 col-md-4 col-lg-3"`
- Long lists: `<q-virtual-scroll :items="store.items" v-slot="{ item }">`
- Navigation: `router.push({ name: 'route-name' })` — never raw paths

### Step 5 — Route Registration (`src/router/routes.ts`)
Add to the correct layout's `children` array:
```typescript
{
  path: '/discover',
  name: 'discover',
  component: () => import('pages/DiscoverPage.vue'),
  meta: { requiresAuth: true }
}
```

### Step 6 — Test (`src/pages/__tests__/<Name>Page.test.ts`)
Three test cases minimum: loading state, error state, data state.

## Verify
```bash
vue-tsc --noEmit
npx eslint src/
quasar build
npx vitest run src/pages/__tests__/<Name>Page.test.ts
```
All must pass before marking the task done.

## Quasar Component Cheatsheet
| Need | Component |
|------|-----------|
| Card | `<q-card>` + `<q-card-section>` |
| List | `<q-list>` + `<q-item>` + `<q-item-section>` |
| Long list | `<q-virtual-scroll>` |
| Image | `<q-img :src="url" :ratio="16/9">` |
| Input | `<q-input v-model="val" outlined>` |
| Select | `<q-select v-model="val" :options="opts" outlined>` |
| Button | `<q-btn label="Click" color="primary" @click="fn">` |
| Toast | `$q.notify({ message: '...', type: 'positive' })` |
| Dialog | `useQuasar().dialog({ ... })` |
| Loading | `<q-spinner>` or `$q.loading.show()` |
| Tabs | `<q-tabs>` + `<q-tab>` + `<q-tab-panels>` |
| Rating | `<q-rating v-model="score" :max="10">` |
| Badge | `<q-badge :label="count" color="primary">` |
