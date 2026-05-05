import { ref } from 'vue'

import { api } from 'src/boot/axios'
import type { MediaSearchItem, MediaSearchResponse } from 'src/types/media'

interface SearchParams {
  query?: string
  type?: string
  page?: number
}

function normalizeResponse(raw: unknown): MediaSearchResponse {
  if (!raw || typeof raw !== 'object') {
    return { items: [], total: 0 }
  }

  const source = raw as Record<string, unknown>
  const itemsRaw = Array.isArray(source.items) ? source.items : []

  const items: MediaSearchItem[] = itemsRaw
    .filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null)
    .map((item) => ({
      id: String(item.id ?? ''),
      title_romaji: String(item.title_romaji ?? item.title ?? 'Untitled'),
      title_english: (item.title_english as string | null | undefined) ?? null,
      cover_image_medium: (item.cover_image_medium as string | null | undefined) ?? null,
      media_type: (item.media_type as string | null | undefined) ?? null,
      format: (item.format as string | null | undefined) ?? null,
      average_score: (item.average_score as number | null | undefined) ?? null,
    }))
    .filter((item) => item.id.length > 0)

  return {
    items,
    total: typeof source.total === 'number' ? source.total : items.length,
    page: typeof source.page === 'number' ? source.page : undefined,
  }
}

export function useMediaSearch() {
  const data = ref<MediaSearchItem[]>([])
  const total = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function search(params: SearchParams): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get('/api/v1/media/search', {
        params: {
          query: params.query,
          type: params.type,
          page: params.page ?? 1,
        },
      })

      const normalized = normalizeResponse(response.data)
      data.value = normalized.items
      total.value = normalized.total
    } catch {
      error.value = 'Failed to fetch media. Please try again.'
      data.value = []
      total.value = 0
    } finally {
      isLoading.value = false
    }
  }

  return {
    data,
    total,
    isLoading,
    error,
    search,
  }
}
