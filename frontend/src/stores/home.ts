import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import { api } from 'src/boot/axios'
import type { HomeSection, FriendActivityItem, GenreItem, ContinueWatchingItem } from 'src/types/home'
import { mapApiMediaToMediaItem, mapApiGenre } from 'src/types/home'
import type { MediaItem } from 'src/types/media'

function emptySection<T = MediaItem>(title: string): HomeSection<T> {
  return { title, items: [], isLoading: false, error: null }
}

export const useHomeStore = defineStore('home', () => {
  // --- Individual sections ---
  const spotlight = ref<HomeSection>(emptySection('Spotlight'))
  const continueWatching = ref<HomeSection<ContinueWatchingItem>>(emptySection<ContinueWatchingItem>('Continue Watching'))
  const trending = ref<HomeSection>(emptySection('Trending Now'))
  const recentUpdates = ref<HomeSection>(emptySection('Recently Updated'))
  const newReleases = ref<HomeSection>(emptySection('New Releases'))
  const friendActivity = ref<HomeSection<FriendActivityItem>>(emptySection<FriendActivityItem>('Friends Watching'))
  const friendActivityOffset = ref(0)
  const friendActivityHasMore = ref(true)
  const friendActivityFilter = ref<string>('all')  // 'all' | 'anime' | 'manga' | 'manhwa'
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
      // Map the list entries — they now have a nested "media" object from the backend
      const items: ContinueWatchingItem[] = (data.items ?? [])
        .filter((entry: Record<string, unknown>) => entry.media)
        .map((entry: Record<string, unknown>) => {
          const media = entry.media as Record<string, unknown>
          const mapped = mapApiMediaToMediaItem(media)
          return {
            ...mapped,
            progress: (entry.progress as number) ?? 0,
            totalEpisodes: (media.episode_count as number | null) ?? null,
          }
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

  async function fetchFriendActivity(
    loadMore: boolean = false,
    mediaType?: string,
  ): Promise<void> {
    // If a new filter is provided (not loadMore), reset pagination
    if (!loadMore && mediaType !== undefined) {
      friendActivityFilter.value = mediaType
      friendActivityOffset.value = 0
      friendActivityHasMore.value = true
      friendActivity.value.items = []
    }

    friendActivity.value.isLoading = true
    friendActivity.value.error = null

    try {
      const params: Record<string, string | number> = { limit: 10 }
      if (friendActivityOffset.value > 0) {
        params.offset = friendActivityOffset.value
      }
      // Only send media_type param if not 'all'
      if (friendActivityFilter.value !== 'all') {
        params.media_type = friendActivityFilter.value
      }

      const { data } = await api.get<{
        items: Record<string, unknown>[]
        total: number
        limit: number
        offset: number
      }>('/api/v1/social/feed', { params })

      const mapped = (data.items ?? []).map(mapActivityItem)

      if (loadMore) {
        friendActivity.value.items = [...friendActivity.value.items, ...mapped]
      } else {
        friendActivity.value.items = mapped
      }

      friendActivityOffset.value += mapped.length
      friendActivityHasMore.value = (data.total ?? 0) > friendActivityOffset.value
      friendActivity.value.error = null
    } catch (e) {
      friendActivity.value.error = extractErrorMessage(e)
      // Friend activity is optional — don't throw
    } finally {
      friendActivity.value.isLoading = false
    }
  }

  /** Convenience wrapper to load more friend activity. */
  async function loadMoreFriendActivity(): Promise<void> {
    await fetchFriendActivity(true)
  }

  /** Change the media type filter and re-fetch. */
  async function setFriendActivityFilter(filter: string): Promise<void> {
    await fetchFriendActivity(false, filter)
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
    friendActivityOffset, friendActivityHasMore, friendActivityFilter,
    anyLoading, anyError, lastFetchedAt, hasData,
    fetchHome,
    fetchSpotlight, fetchContinueWatching, fetchTrending, fetchNewReleases, fetchGenres,
    fetchFriendActivity, loadMoreFriendActivity, setFriendActivityFilter,
  }
})
