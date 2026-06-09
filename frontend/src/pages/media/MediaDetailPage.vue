<template>
  <div class="media-detail-page">
    <!-- Loading state -->
    <div v-if="isLoading" class="page-loading">
      <div class="spinner" />
      <span>Loading media details...</span>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="page-error">
      <p>{{ error }}</p>
      <button @click="fetchMedia">Retry</button>
    </div>

    <template v-else-if="media">
      <!-- Hero banner section -->
      <HeroBanner
        :title="media.title_english || media.title_romaji"
        :titleEnglish="media.title_english ?? null"
        :bannerImage="media.banner_image ?? null"
        :synopsis="media.synopsis ?? null"
        :score="media.average_score ?? null"
        :year="media.season_year ?? null"
        :mediaType="media.media_type ?? 'Unknown'"
        :format="media.format ?? null"
        :status="media.status ?? null"
        :episodeCount="media.episode_count ?? null"
        :genres="media.genres ?? []"
        :isSynopsisExpanded="isSynopsisExpanded"
        @synopsis-toggle="isSynopsisExpanded = !isSynopsisExpanded"
        @play="onPlay"
        @add-list="showAddSheet = true"
        @like="onLike"
        @share="onShare"
      />

      <!-- Tab bar -->
      <div class="tab-bar">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab content -->
      <div class="tab-content">
        <!-- Episodes tab -->
        <div v-if="activeTab === 'episodes'" class="tab-panel">
          <div v-if="serverOptions.length > 0" class="server-selector-section">
            <ServerSelector
              :servers="serverOptions"
              :selectedServerId="selectedServerId"
              :loading="isSourcesLoading"
              :error="sourcesError"
              @select="onServerSelect"
            />
          </div>
          <EpisodeList
            :items="episodes"
            :loading="isEpisodesLoading"
            :error="episodesError"
            :watchedEpisodeNumbers="watchedEpisodes"
            :selectedEpisodeNumber="selectedEpisodeNumber"
            :totalCount="episodes.length"
            :sortOrder="episodeSortOrder"
            :selectedLanguageFilter="selectedLanguageFilter"
            @select="onEpisodeSelect"
            @play="onEpisodePlay"
            @retry="fetchEpisodes"
            @toggle-sort="episodeSortOrder = episodeSortOrder === 'asc' ? 'desc' : 'asc'"
            @language-filter="selectedLanguageFilter = $event"
          />
        </div>

        <!-- Info tab -->
        <div v-if="activeTab === 'info'" class="tab-panel">
          <div class="info-section">
            <!-- Synopsis -->
            <div class="info-block">
              <h3>Synopsis</h3>
              <p class="synopsis-text" :class="{ expanded: isInfoSynopsisExpanded }">
                {{ media.synopsis || 'No synopsis available.' }}
              </p>
              <button
                v-if="media.synopsis && media.synopsis.length > 300"
                class="text-toggle"
                @click="isInfoSynopsisExpanded = !isInfoSynopsisExpanded"
              >
                {{ isInfoSynopsisExpanded ? 'Show less' : 'Read more' }}
              </button>
            </div>

            <!-- Genres -->
            <div v-if="media.genres && media.genres.length > 0" class="info-block">
              <h3>Genres</h3>
              <div class="genre-pills">
                <span v-for="g in media.genres" :key="g" class="genre-chip">{{ g }}</span>
              </div>
            </div>

            <!-- Metadata -->
            <div class="info-block">
              <h3>Details</h3>
              <table class="meta-table">
                <tbody>
                  <tr>
                    <td>Type</td>
                    <td>{{ media.media_type || 'Unknown' }}</td>
                  </tr>
                  <tr>
                    <td>Format</td>
                    <td>{{ media.format || 'Unknown' }}</td>
                  </tr>
                  <tr>
                    <td>Status</td>
                    <td>{{ media.status || 'Unknown' }}</td>
                  </tr>
                  <tr v-if="media.episode_count">
                    <td>Episodes</td>
                    <td>{{ media.episode_count }}</td>
                  </tr>
                  <tr v-if="media.season_year">
                    <td>Season</td>
                    <td>{{ media.season_year }}</td>
                  </tr>
                  <tr>
                    <td>Score</td>
                    <td>{{ media.average_score ?? 'N/A' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Related tab -->
        <div v-if="activeTab === 'related'" class="tab-panel">
          <RelatedMediaCarousel
            :items="relatedMedia"
            :isLoading="isRelatedLoading"
            :error="relatedError"
            @retry="fetchRelated"
            @navigate="onRelatedNavigate"
          />
        </div>
      </div>

      <!-- Add to List sheet -->
      <AddToListSheet
        v-model="showAddSheet"
        :media-id="media.id"
        :title="media.title_english || media.title_romaji"
      />

      <!-- Video player overlay -->
      <Teleport to="body">
        <div v-if="showPlayer" class="player-overlay">
          <div class="player-overlay-header">
            <button class="player-close-btn" @click="closePlayer">✕</button>
            <span class="player-overlay-title">
              {{ media?.title_english || media?.title_romaji }} — Ep {{ playerEpisodeNumber }}
            </span>
            <div class="player-overlay-nav">
              <button
                class="nav-btn"
                :disabled="!hasPreviousEpisode"
                @click="playPrevious"
              >
                ◀ Prev
              </button>
              <button
                class="nav-btn"
                :disabled="!hasNextEpisode"
                @click="playNext"
              >
                Next ▶
              </button>
            </div>
          </div>
          <div class="player-overlay-content">
            <VideoPlayer
              :embedUrl="playerEmbedUrl"
              :title="playerTitle"
              :isLoading="false"
              autoplay
              @ended="onPlayerEnded"
              @retry="reloadPlayer"
            />
          </div>
        </div>
      </Teleport>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AddToListSheet from 'src/components/tracking/AddToListSheet.vue'
import HeroBanner from 'src/components/anime/HeroBanner.vue'
import EpisodeList from 'src/components/anime/EpisodeList.vue'
import ServerSelector from 'src/components/player/ServerSelector.vue'
import RelatedMediaCarousel from 'src/components/anime/RelatedMediaCarousel.vue'
import VideoPlayer from 'src/components/player/VideoPlayer.vue'
import { useMediaDetail } from 'src/composables/useMediaDetail'
import { useTrackingStore } from 'src/stores/tracking'
import { api } from 'src/boot/axios'
import type { EpisodeItem, ServerOption } from 'src/types/media'
import type { WatchStatus } from 'src/types/tracking'

interface RelatedMediaItem {
  id: string
  title: string
  coverImage: string | null
  relationType: string
}

const route = useRoute()
const router = useRouter()
const showAddSheet = ref(false)
const isSynopsisExpanded = ref(false)
const isInfoSynopsisExpanded = ref(false)

// Tab state
const activeTab = ref<'episodes' | 'info' | 'related'>('episodes')
const tabs = [
  { id: 'episodes' as const, label: 'Episodes' },
  { id: 'info' as const, label: 'Info' },
  { id: 'related' as const, label: 'Related' },
]

// Episode state
const episodes = ref<EpisodeItem[]>([])
const isEpisodesLoading = ref(false)
const episodesError = ref<string | null>(null)
const episodeSortOrder = ref<'asc' | 'desc'>('asc')
const selectedLanguageFilter = ref<'all' | 'sub' | 'dub'>('all')
const selectedEpisodeNumber = ref<number | null>(null)
const watchedEpisodes = ref<number[]>([])

// Player overlay state
const showPlayer = ref(false)
const playerEmbedUrl = ref<string | null>(null)
const playerEpisodeNumber = ref<number>(0)
const playerLanguage = ref<'sub' | 'dub'>('sub')
const playerTitle = ref('')

// Source/server state
const serverOptions = ref<ServerOption[]>([])
const selectedServerId = ref<string | null>(null)
const isSourcesLoading = ref(false)
const sourcesError = ref<string | null>(null)

// Related media state
const relatedMedia = ref<RelatedMediaItem[]>([])
const isRelatedLoading = ref(false)
const relatedError = ref<string | null>(null)

// Progress tracking state
const isUpdatingProgress = ref(false)

// Tracking store
const trackingStore = useTrackingStore()

// Main media state
const { data: media, isLoading, error, fetchById } = useMediaDetail()

async function fetchMedia(): Promise<void> {
  const id = route.params.id
  if (typeof id === 'string' && id.length > 0) {
    await fetchById(id)
  }
}

async function fetchEpisodes(): Promise<void> {
  const id = route.params.id
  if (typeof id !== 'string') return
  isEpisodesLoading.value = true
  episodesError.value = null
  try {
    const response = await api.get(`/api/v1/media/${id}/episodes/sources`)
    episodes.value = (response.data.items ?? []).map(mapEpisode)
  } catch {
    episodesError.value = 'Failed to load episodes.'
  } finally {
    isEpisodesLoading.value = false
  }
}

async function fetchSources(): Promise<void> {
  const id = route.params.id
  if (typeof id !== 'string') return
  isSourcesLoading.value = true
  sourcesError.value = null
  try {
    const response = await api.get(`/api/v1/media/${id}/sources`)
    const rawItems = response.data.items ?? response.data ?? []
    serverOptions.value = rawItems.flatMap((m: Record<string, unknown>) => {
      const episodes_list = (m.episodes as Array<Record<string, unknown>>) ?? []
      return episodes_list.map((ep: Record<string, unknown>) => ({
        id: String(ep.id ?? ''),
        source: String(m.source ?? ''),
        language: String(ep.language ?? 'sub'),
        episodeNumber: Number(ep.episode_number ?? 0),
        embedUrl: (ep.embed_url as string | null) ?? null,
        isAvailable: ep.is_available !== false,
      }))
    })
    if (serverOptions.value.length > 0 && !selectedServerId.value) {
      selectedServerId.value = serverOptions.value[0].id
    }
  } catch {
    sourcesError.value = 'Failed to load streaming sources.'
  } finally {
    isSourcesLoading.value = false
  }
}

async function fetchRelated(): Promise<void> {
  const id = route.params.id
  if (typeof id !== 'string') return
  isRelatedLoading.value = true
  relatedError.value = null
  try {
    const response = await api.get(`/api/v1/media/${id}/related`)
    relatedMedia.value = (response.data.items ?? []).map(
      (r: Record<string, unknown>) => ({
        id: String(r.id ?? ''),
        title: String(r.title ?? r.title_romaji ?? 'Unknown'),
        coverImage: (r.cover_image_large as string | null) ?? null,
        relationType: String(r.relation_type ?? 'other'),
      }),
    )
  } catch {
    relatedError.value = 'Failed to load related media.'
  } finally {
    isRelatedLoading.value = false
  }
}

function mapEpisode(raw: Record<string, unknown>): EpisodeItem {
  const sources = (raw.sources as Array<Record<string, unknown>>) ?? []
  const hasSub = sources.some((s) => s.language === 'sub' && s.is_available !== false)
  const hasDub = sources.some((s) => s.language === 'dub' && s.is_available !== false)

  return {
    id: String(raw.id ?? ''),
    episodeNumber: Number(raw.episode_number ?? raw.episodeNumber ?? 0),
    title: (raw.canonical_title as string | null) ?? (raw.title as string | null) ?? null,
    thumbnailUrl: (raw.thumbnail_url as string | null) ?? (raw.thumbnailUrl as string | null) ?? null,
    durationMinutes: (raw.duration_minutes as number | null) ?? (raw.durationMinutes as number | null) ?? null,
    airDate: (raw.canonical_air_date as string | null) ?? (raw.air_date as string | null) ?? (raw.airDate as string | null) ?? null,
    language: hasSub ? 'sub' : hasDub ? 'dub' : null,
    hasSources: sources.length > 0 && sources.some((s) => s.is_available !== false),
  }
}

// Player overlay helpers
const hasPreviousEpisode = computed(() => {
  if (episodes.value.length === 0) return false
  const idx = episodes.value.findIndex((e) => e.episodeNumber === playerEpisodeNumber.value)
  return idx > 0
})

const hasNextEpisode = computed(() => {
  if (episodes.value.length === 0) return false
  const idx = episodes.value.findIndex((e) => e.episodeNumber === playerEpisodeNumber.value)
  return idx >= 0 && idx < episodes.value.length - 1
})

function resolveEmbedUrl(episodeNumber: number): { url: string | null; lang: 'sub' | 'dub' } {
  // Find the first available source for this episode
  for (const ep of episodes.value) {
    if (ep.episodeNumber === episodeNumber) {
      // Try to find a server option matching this episode
      const matching = serverOptions.value.find(
        (s) => s.episodeNumber === episodeNumber && s.isAvailable,
      )
      if (matching) {
        return { url: matching.embedUrl, lang: matching.language as 'sub' | 'dub' }
      }
    }
  }
  return { url: null, lang: 'sub' }
}

function openPlayer(episodeNumber: number): void {
  const { url, lang } = resolveEmbedUrl(episodeNumber)
  playerEmbedUrl.value = url
  playerEpisodeNumber.value = episodeNumber
  playerLanguage.value = lang
  playerTitle.value = `Episode ${episodeNumber}`
  showPlayer.value = true
}

function closePlayer(): void {
  showPlayer.value = false
  playerEmbedUrl.value = null
}

function playNext(): void {
  if (!hasNextEpisode.value) return
  const idx = episodes.value.findIndex((e) => e.episodeNumber === playerEpisodeNumber.value)
  const nextEp = episodes.value[idx + 1]
  if (nextEp) {
    openPlayer(nextEp.episodeNumber)
  }
}

function playPrevious(): void {
  if (!hasPreviousEpisode.value) return
  const idx = episodes.value.findIndex((e) => e.episodeNumber === playerEpisodeNumber.value)
  const prevEp = episodes.value[idx - 1]
  if (prevEp) {
    openPlayer(prevEp.episodeNumber)
  }
}

function reloadPlayer(): void {
  const { url } = resolveEmbedUrl(playerEpisodeNumber.value)
  playerEmbedUrl.value = url
}

async function onPlayerEnded(): Promise<void> {
  const epNum = playerEpisodeNumber.value
  // Prevent double-watch
  if (watchedEpisodes.value.includes(epNum)) return
  watchedEpisodes.value.push(epNum)

  // Persist progress silently — never block user experience on network failure
  try {
    await updateProgressForEpisode(epNum)
  } catch {
    // Silently fail; progress will be synced on next visit
  }

  // Auto-advance to next episode or close
  if (hasNextEpisode.value) {
    playNext()
  } else {
    closePlayer()
  }
}

async function updateProgressForEpisode(episodeNumber: number): Promise<void> {
  if (isUpdatingProgress.value) return
  isUpdatingProgress.value = true
  try {
    const mediaId = route.params.id as string
    const entry = await trackingStore.getEntryByMedia(mediaId)
    if (!entry) {
      await trackingStore.addToList({
        media_id: mediaId,
        status: 'watching' as WatchStatus,
        progress: episodeNumber,
      })
    } else {
      const episodeCount = media.value?.episode_count
      const isLastEpisode = episodeCount != null && episodeNumber >= episodeCount
      await trackingStore.updateEntry(mediaId, {
        progress: episodeNumber,
        ...(isLastEpisode ? { status: 'completed' as WatchStatus } : {}),
      })
    }
  } finally {
    isUpdatingProgress.value = false
  }
}

function onPlay(): void {
  // Triggers when Play button clicked in HeroBanner
  // Default to first episode
  if (episodes.value.length > 0) {
    openPlayer(episodes.value[0].episodeNumber)
  }
}

function onEpisodeSelect(episodeNumber: number): void {
  selectedEpisodeNumber.value = episodeNumber
}

function onEpisodePlay(episodeNumber: number): void {
  selectedEpisodeNumber.value = episodeNumber
  openPlayer(episodeNumber)
}

function onServerSelect(serverId: string): void {
  selectedServerId.value = serverId
}

function onLike(): void {
  // Placeholder — future feature
}

function onShare(): void {
  // Placeholder — future feature
}

function onRelatedNavigate(id: string): void {
  router.push({ name: 'media-detail', params: { id } }).catch(() => undefined)
}

onMounted(async () => {
  await fetchMedia()
  if (media.value) {
    await Promise.allSettled([
      fetchEpisodes(),
      fetchSources(),
      fetchRelated(),
    ])
  }
})
</script>

<style lang="scss">
@use 'src/css/tokens' as *;

.media-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: $space-4;

  .page-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    gap: $space-3;
    color: $text-muted;

    .spinner {
      width: 42px;
      height: 42px;
      border: 3px solid $bg-hover;
      border-top-color: $accent-primary;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }
  }

  .page-error {
    text-align: center;
    padding: $space-8;
    color: $text-muted;

    p {
      margin: 0 0 $space-4;
      color: $accent-error;
    }

    button {
      padding: $space-2 $space-5;
      background: $accent-primary;
      color: white;
      border: none;
      border-radius: $radius-md;
      cursor: pointer;
      font-size: $font-size-sm;
      font-weight: 600;
    }
  }

  .tab-bar {
    display: flex;
    gap: $space-1;
    margin-bottom: $space-6;
    border-bottom: 1px solid $border-default;

    .tab-btn {
      padding: $space-3 $space-5;
      background: none;
      border: none;
      border-bottom: 2px solid transparent;
      color: $text-muted;
      font-size: $font-size-sm;
      font-weight: 600;
      cursor: pointer;
      transition: all $transition;

      &:hover {
        color: $text-primary;
      }

      &.active {
        color: $accent-primary;
        border-bottom-color: $accent-primary;
      }
    }
  }

  .tab-content {
    .tab-panel {
      min-height: 200px;
    }

    .server-selector-section {
      margin-bottom: $space-6;
    }

    .info-section {
      display: flex;
      flex-direction: column;
      gap: $space-6;

      .info-block {
        h3 {
          font-size: $font-size-md;
          font-weight: 700;
          color: $text-primary;
          margin: 0 0 $space-3;
        }

        .synopsis-text {
          font-size: $font-size-sm;
          color: $text-secondary;
          line-height: 1.7;
          margin: 0;

          &:not(.expanded) {
            display: -webkit-box;
            -webkit-line-clamp: 6;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
        }

        .text-toggle {
          background: none;
          border: none;
          color: $accent-primary;
          cursor: pointer;
          font-size: $font-size-sm;
          font-weight: 600;
          padding: $space-1 0;
          margin-top: $space-1;

          &:hover {
            text-decoration: underline;
          }
        }

        .genre-pills {
          display: flex;
          flex-wrap: wrap;
          gap: $space-2;

          .genre-chip {
            padding: 4px 12px;
            border-radius: 999px;
            font-size: $font-size-xs;
            font-weight: 500;
            background: rgba($accent-primary, 0.15);
            color: $accent-primary;
          }
        }

        .meta-table {
          width: 100%;
          max-width: 400px;

          td {
            padding: $space-2 $space-3;
            font-size: $font-size-sm;
            border-bottom: 1px solid $border-subtle;

            &:first-child {
              color: $text-muted;
              font-weight: 500;
              width: 100px;
            }

            &:last-child {
              color: $text-primary;
            }
          }
        }
      }
    }
  }
}

.player-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: black;
  display: flex;
  flex-direction: column;

  .player-overlay-header {
    display: flex;
    align-items: center;
    gap: $space-3;
    padding: $space-3 $space-4;
    background: $bg-primary;
    border-bottom: 1px solid $border-subtle;
    z-index: 1;

    .player-close-btn {
      background: none;
      border: none;
      color: $text-secondary;
      font-size: $font-size-lg;
      cursor: pointer;
      padding: $space-1;
      line-height: 1;

      &:hover {
        color: $text-primary;
      }
    }

    .player-overlay-title {
      flex: 1;
      font-size: $font-size-sm;
      color: $text-secondary;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .player-overlay-nav {
      display: flex;
      gap: $space-2;

      .nav-btn {
        padding: $space-1 $space-3;
        border-radius: $radius-md;
        border: $border-subtle;
        background: $bg-secondary;
        color: $text-primary;
        font-size: $font-size-xs;
        font-weight: 600;
        cursor: pointer;

        &:hover:not(:disabled) {
          border-color: $accent-primary;
          color: $accent-primary;
        }

        &:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }
      }
    }
  }

  .player-overlay-content {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: black;

    .video-player {
      width: 100%;
      height: 100%;
      max-width: 1200px;
      max-height: 90vh;
      aspect-ratio: auto;
    }
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
