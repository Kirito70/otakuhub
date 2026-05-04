---
name: quasar-page
description: Scaffold a complete Quasar page with TypeScript types, Pinia store, responsive layout, loading/error/data states, and Vitest component test.
---

# Quasar Page Scaffold

## Steps

1. **Read context**: Read `docs/quasar-architecture.md` and the relevant feature spec.

2. **Create types** in `src/types/<name>.ts`:
   All interfaces for this feature. No `any`. Export everything.

3. **Create Pinia store** in `src/stores/<name>.ts`:
   Setup syntax. Async actions with `isLoading`, `error`, data refs.
   Axios calls to FastAPI backend only.

4. **Create page** in `src/pages/<Name>Page.vue`:
   - `<script setup lang="ts">`
   - Three states: loading (`q-spinner`), error (`q-banner`), content
   - Responsive grid: `col-12 col-sm-6 col-md-4`
   - Long lists: `q-virtual-scroll`

5. **Register route** in `src/router/routes.ts`:
   Named route, correct layout, `meta: { requiresAuth: true }` if needed.

6. **Create test** in `src/pages/__tests__/<Name>Page.test.ts`:
   - loading state renders spinner
   - error state renders banner
   - data state renders content

7. **Verify**:
   ```bash
   vue-tsc --noEmit
   npx eslint src/pages/ src/stores/
   quasar build
   npx vitest run src/pages/__tests__/
   ```
   Zero errors before reporting done.
