import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import { api } from 'src/boot/axios'
import type { HomeSection, FriendActivityItem, GenreItem } from 'src/types/home'
import { mapApiMediaToMediaItem, mapApiGenre } from 'src/types/home'
import type { MediaItem } from 'src/types/media'

function emptySection<T = MediaItem>(title: string): HomeSection<T> {
  return { title, items: [], isLoading: false, error: null }
}

export const useHomeStore = defineStore('home', () => {
  // --- Individual sections ---
  const spotlight = ref<HomeSection>(emptySection('Spotlight'))
  const continueWatching = ref<HomeSection>(emptySection('Continue Watching'))
  const trending = ref<HomeSection>(emptySection('Trending Now'))
  const recentUpdates = ref<HomeSection>(emptySection('Recently Updated'))
  const newReleases = ref<HomeSection>(emptySection('New Releases'))
  const friendActivity = ref<HomeSection<FriendActivityItem>>(emptySection<FriendActivityItem>('Friends Watching'))
  const genres = ref<HomeSection<GenreItem>>(emptySection<GenreItem>('Popular Genres'))

  // --- Aggregate loading/error ---
  const anyLoading = ref(false)
  const anyError = ref<string | null>(null)
  const lastFetchedAt = ref<number>(0)

  // --- Computed ---
  const hasData = computed(() =>
    spotlight.value.items.length > 0 ||
    continueWatching.value.items.length > 0 ||
    trending.value.items.length > 0 ||
    recentUpdates.value.items.length > 0 ||
    newReleases.value.items.length > 0 ||
    friendActivity.value.items.length > 0 ||
    genres.value.items.length > 0
  )

  // ===== Fetch all sections =====

  async function fetchHome(): Promise<void> {
    anyLoading.value = true
    anyError.value = null

    // Mark all sections as loading
    spotlight.value.isLoading = true
    continueWatching.value.isLoading = true
    trending.value.isLoading = true
    recentUpdates.value.isLoading = true
    newReleases.value.isLoading = true
    friendActivity.value.isLoading = true
    genres.value.isLoading = true

    try {
      // Fire all requests in parallel
      const results = await Promise.allSettled([
        fetchSpotlight(),
        fetchContinueWatching(),
        fetchTrending(),
        fetchRecentUpdates(),
        fetchNewReleases(),
        fetchFriendActivity(),
        fetchGenres(),
      ])

      // Collect errors
      const errors: string[] = []
      for (const result of results) {
        if (result.status === 'rejected') {
          errors.push(result.reason?.message ?? String(result.reason))
        }
      }

      if (errors.length > 0) {
        anyError.value = errors.join('; ')
      }

      lastFetchedAt.value = Date.now()
    } finally {
      anyLoading.value = false
    }
  }

  // ===== Individual section fetchers =====

  async function fetchSpotlight(): Promise<void> {
    try {
      const { data } = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/media/trending', {
        params: { limit: 5 },
      })
      spotlight.value.items = (data.items ?? []).map(mapApiMediaToMediaItem)
      spotlight.value.error = null
    } catch (e) {
      spotlight.value.error = extractErrorMessage(e)
      throw e
    } finally {
      spotlight.value.isLoading = false
    }
  }

  async function fetchContinueWatching(): Promise<void> {
    try {
      const { data } = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/lists/me', {
        params: { statuses: 'watching,reading', limit: 20 },
      })
      // Map the list entries — they have media fields nested
      const items = (data.items ?? [])
        .filter((entry: Record<string, unknown>) => entry.media_id || entry.media)
        .map((entry: Record<string, unknown>) => {
          const media = (entry.media ?? entry) as Record<string, unknown>
          const mapped = mapApiMediaToMediaItem(media)
          // Add progress info
          return { ...mapped, progress: entry.progress as number ?? 0 }
        })
      continueWatching.value.items = items
      continueWatching.value.error = null
    } catch (e) {
      continueWatching.value.error = extractErrorMessage(e)
      // Continue Watching is optional — don't throw, just return empty
    } finally {
      continueWatching.value.isLoading = false
    }
  }

  async function fetchTrending(): Promise<void> {
    try {
      const { data } = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/media/trending', {
        params: { limit: 24 },
      })
      trending.value.items = (data.items ?? []).map(mapApiMediaToMediaItem)
      trending.value.error = null
    } catch (e) {
      trending.value.error = extractErrorMessage(e)
      throw e
    } finally {
      trending.value.isLoading = false
    }
  }

  async function fetchRecentUpdates(): Promise<void> {
    try {
      // Try recent-updates if available; fall back to seasonal
      let data: { items: Record<string, unknown>[] }
      try {
        const res = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/media/recent-updates', {
          params: { limit: 20 },
        })
        data = res.data
      } catch {
        // Fallback: seasonal endpoint
        const res = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/media/seasonal', {
          params: { limit: 20 },
        })
        data = res.data
      }
      recentUpdates.value.items = (data.items ?? []).map(mapApiMediaToMediaItem)
      recentUpdates.value.error = null
    } catch (e) {
      recentUpdates.value.error = extractErrorMessage(e)
      throw e
    } finally {
      recentUpdates.value.isLoading = false
    }
  }

  async function fetchNewReleases(): Promise<void> {
    try {
      const { data } = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/media/popular', {
        params: { limit: 12 },
      })
      newReleases.value.items = (data.items ?? []).map(mapApiMediaToMediaItem)
      newReleases.value.error = null
    } catch (e) {
      newReleases.value.error = extractErrorMessage(e)
      throw e
    } finally {
      newReleases.value.isLoading = false
    }
  }

  async function fetchFriendActivity(): Promise<void> {
    try {
      const { data } = await api.get<{ items: Record<string, unknown>[] }>('/api/v1/social/feed', {
        params: { limit: 10 },
      })
      friendActivity.value.items = (data.items ?? []).map(mapActivityItem)
      friendActivity.value.error = null
    } catch (e) {
      friendActivity.value.error = extractErrorMessage(e)
      // Friend activity is optional
    } finally {
      friendActivity.value.isLoading = false
    }
  }

  async function fetchGenres(): Promise<void> {
    try {
      const res = await api.get<GenreItem[] | { items: Record<string, unknown>[] }>('/api/v1/media/genres')
      // Handle both array response and {items: [...]} envelope
      const rawItems = Array.isArray(res.data) ? res.data : ((res.data as { items: Record<string, unknown>[] }).items ?? [])
      genres.value.items = rawItems.map((g: Record<string, unknown>) => mapApiGenre(g))
      genres.value.error = null
    } catch (e) {
      genres.value.error = extractErrorMessage(e)
      throw e
    } finally {
      genres.value.isLoading = false
    }
  }

  // ===== Helpers =====

  function extractErrorMessage(e: unknown): string {
    if (e && typeof e === 'object' && 'message' in e) return String((e as { message: string }).message)
    if (e && typeof e === 'object' && 'response' in e) {
      const resp = (e as { response: { data?: { detail?: string } } }).response
      return resp?.data?.detail ?? 'Request failed'
    }
    return String(e)
  }

  function mapActivityItem(raw: Record<string, unknown>): FriendActivityItem {
    return {
      id: String(raw.id ?? ''),
      userId: String(raw.user_id ?? ''),
      username: String(raw.username ?? ''),
      displayName: (raw.display_name as string) ?? null,
      avatarUrl: (raw.avatar_url as string) ?? null,
      mediaId: String(raw.media_id ?? ''),
      mediaTitle: String(raw.media_title ?? ''),
      mediaCoverImage: (raw.media_cover_image as string) ?? null,
      eventType: String(raw.event_type ?? ''),
      newStatus: (raw.new_status as string) ?? null,
      newProgress: (raw.new_progress as number) ?? null,
      createdAt: String(raw.created_at ?? ''),
    }
  }

  return {
    spotlight, continueWatching, trending, recentUpdates,
    newReleases, friendActivity, genres,
    anyLoading, anyError, lastFetchedAt, hasData,
    fetchHome,
    fetchSpotlight, fetchTrending, fetchNewReleases, fetchGenres,
  }
})
