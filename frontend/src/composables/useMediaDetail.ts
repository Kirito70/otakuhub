import { ref } from 'vue'

import { api } from 'src/boot/axios'

export interface MediaDetail {
  id: string
  title_romaji: string
  title_english?: string | null
  title_native?: string | null
  synopsis?: string | null
  media_type?: string | null
  format?: string | null
  status?: string | null
  average_score?: number | null
  cover_image_large?: string | null
  banner_image?: string | null
}

function normalizeDetail(raw: unknown): MediaDetail | null {
  if (!raw || typeof raw !== 'object') {
    return null
  }

  const item = raw as Record<string, unknown>
  if (!item.id) {
    return null
  }

  return {
    id: String(item.id),
    title_romaji: String(item.title_romaji ?? item.title ?? 'Untitled'),
    title_english: (item.title_english as string | null | undefined) ?? null,
    title_native: (item.title_native as string | null | undefined) ?? null,
    synopsis: (item.synopsis as string | null | undefined) ?? null,
    media_type: (item.media_type as string | null | undefined) ?? null,
    format: (item.format as string | null | undefined) ?? null,
    status: (item.status as string | null | undefined) ?? null,
    average_score: (item.average_score as number | null | undefined) ?? null,
    cover_image_large: (item.cover_image_large as string | null | undefined) ?? null,
    banner_image: (item.banner_image as string | null | undefined) ?? null,
  }
}

export function useMediaDetail() {
  const data = ref<MediaDetail | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  async function fetchById(id: string): Promise<void> {
    isLoading.value = true
    error.value = null

    try {
      const response = await api.get(`/api/v1/media/${id}`)
      data.value = normalizeDetail(response.data)

      if (!data.value) {
        error.value = 'Media detail payload is invalid.'
      }
    } catch {
      error.value = 'Failed to load media detail.'
      data.value = null
    } finally {
      isLoading.value = false
    }
  }

  return {
    data,
    isLoading,
    error,
    fetchById,
  }
}
