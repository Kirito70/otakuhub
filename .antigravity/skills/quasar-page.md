---
name: vue-page
description: Scaffold a complete Vue 3 page with TypeScript types, Pinia store, Tailwind responsive layout, loading/error/data states, and Vitest component test.
---

# Vue 3 Page Scaffold (Tailwind + shadcn-vue)

## Steps

1. **Read context**: Read `docs/frontend-architecture.md` and the relevant feature spec.

2. **Create types** in `src/types/<name>.ts`:
   All interfaces for this feature. No `any`. Export everything.

3. **Create Pinia store** in `src/stores/<name>.ts`:
   Setup syntax. Async actions with `isLoading`, `error`, data refs.
   Axios calls to FastAPI backend only.

4. **Create page** in `src/pages/<Name>Page.vue`:
   - `<script setup lang="ts">`
   - Three states: loading (`<Skeleton>`), error (`<AppEmptyState mode="error">`), content
   - Responsive: Tailwind grid `grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4`
   - Long lists: infinite scroll with `<IntersectionObserver>` or scroll-based pagination
   - Use shadcn-vue primitives: `<Button>`, `<Card>`, `<Input>`, `<Badge>`, `<Tabs>`, `<Dialog>`, etc.
   - Dark theme: bg `#0a0a0a`, text white (no Quasar `$q` references)

5. **Register route** in `src/router/routes.ts`:
   Named route, correct layout, `meta: { requiresAuth: true }` if needed.

6. **Create test** in `src/pages/__tests__/<Name>Page.test.ts`:
   - loading state renders Skeleton
   - error state renders AppEmptyState
   - data state renders content

7. **Verify**:
   ```bash
   vue-tsc --noEmit
   npx eslint src/pages/ src/stores/
   vite build
   npx vitest run src/pages/__tests__/
   ```
   Zero errors before reporting done.
