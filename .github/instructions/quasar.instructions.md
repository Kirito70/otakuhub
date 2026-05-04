---
applyTo: "frontend/**"
---
# Frontend Copilot Instructions (Quasar / Vue 3 / TypeScript)

Always use `<script setup lang="ts">`. Never use Options API or defineComponent.
Props: `defineProps<{ propName: PropType }>()`. Emits: `defineEmits<{ eventName: [arg: Type] }>()`.
State: Pinia stores in `src/stores/`. Use Setup Store syntax (not Options syntax).
HTTP: `import { api } from 'src/boot/axios'` — never fetch() or raw axios import.
Routing: named routes only — `router.push({ name: 'route-name', params: { id } })`.
Lists > 100 items: always `QVirtualScroll` — never plain `v-for` on a `<div>`.
Responsive: Quasar grid classes (`col-12 col-sm-6 col-md-4`) and `$q.screen` — not CSS media queries.
Notifications: `$q.notify({ message, type })` — no custom toast components.
Images: `<q-img>` with `:ratio` and error slot — never `<img>` for remote URLs.
TypeScript strict — no `any`, no `as SomeType` casts without a comment.
Never call AniList, MangaDex, or Jikan from frontend code. All API calls → FastAPI backend.
