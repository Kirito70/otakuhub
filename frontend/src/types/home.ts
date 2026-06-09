import type { MediaItem } from 'src/types/media'

export interface HomeSection<T = MediaItem> {
  title: string
  items: T[]
  isLoading: boolean
  error: string | null
}

export interface HomePageState {
  spotlight: HomeSection
  continueWatching: HomeSection
  trending: HomeSection
  recentUpdates: HomeSection
  newReleases: HomeSection
  friendActivity: HomeSection<FriendActivityItem>
  genres: HomeSection<GenreItem>
}

export interface FriendActivityItem {
  id: string
  userId: string
  username: string
  displayName: string | null
  avatarUrl: string | null
  mediaId: string
  mediaTitle: string
  mediaCoverImage: string | null
  eventType: string
  newStatus: string | null
  newProgress: number | null
  createdAt: string
}

export interface GenreItem {
  id: string
  name: string
  slug: string
}

/** Maps a raw API media object (snake_case) to MediaItem (camelCase). */
export function mapApiMediaToMediaItem(raw: Record<string, unknown>): MediaItem {
  return {
    id: String(raw.id ?? ''),
    title: String(raw.title_romaji ?? raw.title_english ?? 'Unknown'),
    coverImage: (raw.cover_image_medium as string) ?? (raw.cover_image_large as string) ?? null,
    mediaType: String(raw.media_type ?? ''),
    format: (raw.format as string) ?? null,
    score: (raw.average_score as number) ?? null,
    year: (raw.season_year as number) ?? null,
    episodeCount: (raw.episode_count as number) ?? null,
    titleEnglish: (raw.title_english as string) ?? null,
    coverImageLarge: (raw.cover_image_large as string) ?? null,
    season: (raw.season as string) ?? null,
    status: (raw.status as string) ?? null,
    synopsis: (raw.synopsis as string) ?? null,
  }
}

/** Maps raw API genre object to GenreItem. */
export function mapApiGenre(item: Record<string, unknown>): GenreItem {
  return {
    id: String(item.id ?? ''),
    name: String(item.name ?? ''),
    slug: String(item.slug ?? ''),
  }
}
