---
name: vue-dev
description: Build a Vue 3 + Tailwind CSS + shadcn-vue feature: TypeScript types, Pinia store, page component, shared components, route registration, and Vitest component test.
---

# Vue 3 Feature Development Skill

## Tech Stack Summary
- **Framework**: Vue 3.5+ with `<script setup lang="ts">`
- **Build**: Vite 6+ (`vite dev` / `vite build`)
- **Styling**: Tailwind CSS v4 (utility classes, `dark:` strategy)
- **Primitives**: shadcn-vue (`<Button>`, `<Card>`, `<Input>`, `<Badge>`, `<Tabs>`, `<Dialog>`, `<Sheet>`, `<Select>`, `<DropdownMenu>`, `<Tooltip>`, `<Avatar>`, `<Skeleton>`, `<Separator>`)
- **State**: Pinia with `pinia-plugin-persistedstate`
- **Router**: vue-router 4.x with named routes
- **HTTP**: Axios with auth interceptor
- **Validation**: zod schemas
- **Desktop**: Electron via `electron-vite`
- **Tests**: Vitest + jsdom + `@vue/test-utils`

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
- Use Tailwind utility classes for all styling
- Use shadcn-vue primitives: `<Card>`, `<Badge>`, `<Button>`, `<Avatar>`, `<Skeleton>`
- Responsive images: `<img :src="url" class="aspect-2/3 rounded-lg object-cover">`
- Dark mode: use `dark:` prefix on classes

### Step 4 — Page (`src/pages/<Name>Page.vue`)
- Always: loading state → error state → content
- Use `<Skeleton>` for loading placeholders
- Use `<AppEmptyState>` for empty/error states
- Responsive: Tailwind `sm:`, `md:`, `lg:` grid classes
  ```html
  <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
  ```
- Navigation: `router.push({ name: 'route-name' })` — never raw paths

### Step 5 — Route Registration (`src/router/routes.ts`)
Add to the correct layout's `children` array:
```typescript
{
  path: '/discover',
  name: 'discover',
  component: () => import('pages/discover/DiscoverPage.vue'),
  meta: { requiresAuth: true }
}
```

### Step 6 — Test (`src/pages/__tests__/<Name>Page.test.ts`)
Three test cases minimum: loading state, error state, data state.

## Verify
```bash
vue-tsc --noEmit
npx eslint src/
vite build
npx vitest run src/pages/__tests__/<Name>Page.test.ts
```
All must pass before marking the task done.

## shadcn-vue Component Cheatsheet
| Need | Component |
|------|-----------|
| Card | `<Card>` + `<CardHeader>` + `<CardTitle>` + `<CardContent>` |
| Button | `<Button variant="default|destructive|outline|secondary|ghost|link">` |
| Input | `<Input v-model="val" />` (wrap in form + zod validation) |
| Select | `<Select>` + `<SelectTrigger>` + `<SelectValue>` + `<SelectContent>` + `<SelectItem>` |
| Tabs | `<Tabs>` + `<TabsList>` + `<TabsTrigger>` + `<TabsContent>` |
| Dialog | `<Dialog>` + `<DialogTrigger>` + `<DialogContent>` + `<DialogHeader>` + `<DialogTitle>` + `<DialogDescription>` |
| Sheet (drawer) | `<Sheet>` + `<SheetTrigger>` + `<SheetContent>` + `<SheetHeader>` + `<SheetTitle>` |
| Dropdown | `<DropdownMenu>` + `<DropdownMenuTrigger>` + `<DropdownMenuContent>` + `<DropdownMenuItem>` |
| Badge | `<Badge variant="default|secondary|destructive|outline">` |
| Avatar | `<Avatar>` + `<AvatarImage>` + `<AvatarFallback>` |
| Separator | `<Separator class="..." />` |
| Skeleton | `<Skeleton class="h-4 w-48" />` |

## Tailwind CSS Patterns

### Responsive breakpoints
```html
<!-- Mobile: 2 cols, Tablet: 3 cols, Desktop: 4 cols -->
<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
```

### Dark mode (always on — dark-only design)
```html
<div class="bg-[#0a0a0a] text-white">
```
No need for `dark:` prefix — OtakuHub is a dark-only streaming app.

### Gradient overlays (aniwave-style)
```html
<div class="absolute inset-0 bg-gradient-to-t from-[#0a0a0a] via-transparent to-transparent"></div>
```

### Hover overlay on cards
```html
<div class="relative group">
  <img ... class="... group-hover:scale-105 transition-transform duration-300">
  <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
    <!-- play button overlay -->
  </div>
</div>
```

### Loading skeletons
```html
<Skeleton class="h-48 w-full rounded-lg" />
<Skeleton class="h-4 w-3/4 mt-2" />
<Skeleton class="h-4 w-1/2 mt-1" />
```

## Form Validation Pattern
```typescript
import { ref } from 'vue'
import { z } from 'zod'

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
})

type LoginForm = z.infer<typeof loginSchema>

const form = ref<LoginForm>({ username: '', password: '' })
const errors = ref<Partial<Record<keyof LoginForm, string>>>({})

function validate(): boolean {
  const result = loginSchema.safeParse(form.value)
  if (!result.success) {
    errors.value = Object.fromEntries(
      result.error.errors.map(e => [e.path[0], e.message])
    )
    return false
  }
  errors.value = {}
  return true
}
```

## Color Reference (aniwaves.ru Dark Theme)
| CSS variable | Value | Usage |
|---|---|---|
| `--bg-primary` | `#0a0a0a` | Page bg |
| `--bg-secondary` | `#111111` | Card bg |
| `--bg-elevated` | `#1a1a1a` | Modal/dropdown bg |
| `--accent` | `#a855f7` | Purple accent |
| `--accent-cyan` | `#06b6d4` | Cyan accent |
| `--text-muted` | `#6b7280` | Muted text |
| `--border` | `#1f2937` | Borders |

Available as Tailwind arbitrary values: `bg-[#0a0a0a]`, `text-[#a855f7]`, etc.

## Build Commands
```bash
vite dev                # Development server (hot reload)
vite build              # Production build → dist/
npm run dev:electron    # Electron dev
npm run build:electron  # Electron production build
npx vitest run          # Run all tests
vue-tsc --noEmit        # Type check
npx eslint src/         # Lint
```

## Important Notes
- Never use `$q` or Quasar API — it's been removed (see ADR 090)
- All imports from `@quasar/` are invalid — use shadcn-vue primitives instead
- Use `import.meta.env.VITE_*` for environment variables (not `process.env`)
- All custom streaming components (AnimeCard, HeroBanner, EpisodeList, VideoPlayer, TrendingCarousel) are pure Vue 3 — they work as-is
- SCSS has been migrated to Tailwind — use utility classes instead of SCSS variables
