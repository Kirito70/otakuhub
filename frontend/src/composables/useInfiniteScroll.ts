import { ref, type Ref } from 'vue'

type FetchFn<T> = (limit: number, offset: number) => Promise<{ items: T[]; total: number }>

/**
 * Composable for paginated lists with infinite-scroll / load-more semantics.
 * Provides pagination state and a loadMore function that appends results.
 */
export function useInfiniteScroll<T>(fetchFn: FetchFn<T>, pageSize = 50) {
  const items = ref<T[]>([]) as Ref<T[]>
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const offset = ref(0)
  const hasMore = ref(true)

  async function loadMore(): Promise<void> {
    if (isLoading.value || !hasMore.value) return

    isLoading.value = true
    error.value = null

    try {
      const result = await fetchFn(pageSize, offset.value)
      items.value = [...items.value, ...result.items]
      total.value = result.total
      offset.value += result.items.length
      hasMore.value = items.value.length < result.total
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load'
    } finally {
      isLoading.value = false
    }
  }

  function reset(): void {
    items.value = []
    offset.value = 0
    total.value = 0
    hasMore.value = true
    error.value = null
    isLoading.value = false
  }

  return {
    items,
    isLoading,
    error,
    total,
    offset,
    hasMore,
    loadMore,
    reset,
  }
}
