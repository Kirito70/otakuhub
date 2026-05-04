---
name: pinia-store
description: Create a typed Pinia setup store with async actions, loading/error states, and optional persistence.
---

# Pinia Store Creation

## Decision Tree

| Use case | Pattern |
|----------|---------|
| Read-only data, auto-fetch on mount | `ref` + `fetchX()` action called from page |
| List with CRUD operations | `ref<Item[]>` + `fetch`, `add`, `update`, `remove` actions |
| Single item detail (by ID) | `ref<Item \| null>` + `fetchById(id)` |
| Auth / global state | Add `persist: true` via pinia-plugin-persistedstate |
| Derived/computed data | `computed(() => state.filter(...))` |

## Template

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from 'src/boot/axios'
import type { MyType } from 'src/types/myType'

export const useMyStore = defineStore('my-store', () => {
  // State
  const items = ref<MyType[]>([])
  const selectedItem = ref<MyType | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const completedItems = computed(() =>
    items.value.filter(i => i.status === 'completed')
  )

  // Actions
  async function fetchItems() {
    isLoading.value = true
    error.value = null
    try {
      const { data } = await api.get<{ items: MyType[] }>('/api/v1/my-endpoint')
      items.value = data.items
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load'
    } finally {
      isLoading.value = false
    }
  }

  async function addItem(payload: Omit<MyType, 'id'>) {
    const { data } = await api.post<MyType>('/api/v1/my-endpoint', payload)
    items.value.push(data)
    return data
  }

  async function updateItem(id: string, payload: Partial<MyType>) {
    const { data } = await api.patch<MyType>(`/api/v1/my-endpoint/${id}`, payload)
    const idx = items.value.findIndex(i => i.id === id)
    if (idx !== -1) items.value[idx] = data
    return data
  }

  async function removeItem(id: string) {
    await api.delete(`/api/v1/my-endpoint/${id}`)
    items.value = items.value.filter(i => i.id !== id)
  }

  function $reset() {
    items.value = []
    selectedItem.value = null
    isLoading.value = false
    error.value = null
  }

  return {
    items, selectedItem, isLoading, error,
    completedItems,
    fetchItems, addItem, updateItem, removeItem, $reset
  }
})
```

## Persistence (for auth store)
```typescript
export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(null)
  const user = ref<User | null>(null)
  // ... actions
  return { accessToken, user }
}, {
  persist: true  // requires pinia-plugin-persistedstate in boot/pinia.ts
})
```

## After Creating Store
```bash
vue-tsc --noEmit    # confirm types are valid
```
The store is ready to import: `const store = useMyStore()`
