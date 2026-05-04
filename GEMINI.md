# Gemini / Antigravity Instructions — OtakuHub

> This file extends AGENTS.md. Read AGENTS.md first.

## Antigravity Agent Configuration

### Primary Role in This Project
Antigravity / Gemini is the **Quasar/Vue frontend specialist** for OtakuHub.
Focus areas: Quasar pages, components, Pinia stores, Axios composables, responsive layout.

### Autonomy Profile
Use **Agent-Assisted** mode (not full autopilot) for this project.
- Plan first for any change touching more than 2 files
- Ask for confirmation before modifying: `src/router/routes.ts`, `quasar.config.ts`, any Pinia store
- Auto-execute safe operations: linting, page creation, composable generation

### Skills Available (`.antigravity/skills/`)
- `quasar-page.md` — Scaffold a new Quasar page with Pinia store and tests
- `pinia-store.md` — Create a typed Pinia store with async actions

### Workflow Slash Commands
Use `/startcycle <feature>` to trigger the full frontend dev pipeline:
1. PM agent reads spec → writes user stories
2. UI Designer describes screen layout using Quasar component names
3. Quasar Engineer implements the page + store
4. Test agent writes Vitest component tests
5. Reviewer checks against AGENTS.md conventions

### Quasar-Specific Rules for Gemini
- All components: `<script setup lang="ts">` — no Options API, no `defineComponent`
- State: Pinia stores — no Vuex, no component-level `ref` for shared data
- HTTP: Axios via `src/boot/axios.ts` — no direct `fetch()` calls
- Routing: `vue-router` 4 with typed routes from `src/router/routes.ts`
- Layout: Quasar's `QLayout` + `QPageContainer` + `QPage` — not custom div structures
- Responsive: `$q.screen.lt.md` / `$q.screen.gt.sm` — not raw CSS breakpoints
- Icons: `@quasar/extras` (Material Icons) — `icon="img:..."` for custom SVGs
- Notifications: `$q.notify()` for toasts — not custom snackbar components
- Loading: `$q.loading.show()` / `.hide()` for full-screen loading
- Lists: `QVirtualScroll` for long lists (100+ items) — not `v-for` on bare arrays
- All images: `q-img` component — not `<img>` tags

### After Building a Page
```bash
cd frontend
vue-tsc --noEmit          # zero TS errors
npx eslint src/           # zero lint errors
quasar build              # confirm SPA build succeeds
```

### Build Targets Reference
```bash
# Web SPA (primary)
quasar build

# PWA
quasar build -m pwa

# Electron (Windows + Linux desktop)
quasar build -m electron

# Android (via Capacitor)
quasar build -m capacitor -T android

# iOS (via Capacitor, requires Mac)
quasar build -m capacitor -T ios
```
