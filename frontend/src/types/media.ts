export interface MediaSearchItem {
  id: string
  title_romaji: string
  title_english?: string | null
  cover_image_medium?: string | null
  media_type?: string | null
  format?: string | null
  status?: string | null
  average_score?: number | null
}

export interface MediaSearchResponse {
  items: MediaSearchItem[]
  total: number
  page?: number
}

// ── Streaming Components (Phase 26) ────────────────────────────────────────

/** Full media item for card/grid/hero display. */
export interface MediaItem {
  id: string
  title: string
  titleEnglish: string | null
  coverImage: string | null
  coverImageLarge: string | null
  mediaType: string
  format: string | null
  score: number | null
  year: number | null
  episodeCount: number | null
  season: string | null
  status: string | null
  synopsis: string | null
}

/** Single episode item for episode list display (Phase 26). */
export interface EpisodeItem {
  id: string
  episodeNumber: number
  title: string | null
  thumbnailUrl: string | null
  durationMinutes: number | null
  airDate: string | null
  language?: 'sub' | 'dub' | null
  hasSources?: boolean
}

/** Source provider mapping for a media title (Phase 26). */
export interface SourceOption {
  id: string
  source: string
  sourceMediaId: string
  sourceUrl: string | null
  mappingStatus: string
  isStreamingEnabled: boolean
  hasSub: boolean
  hasDub: boolean
  episodeCount: number | null
}

/** Server/mirror option for the ServerSelector (Phase 26). */
export interface ServerOption {
  id: string
  source: string
  language: string
  episodeNumber: number
  embedUrl: string | null
  isAvailable: boolean
}
