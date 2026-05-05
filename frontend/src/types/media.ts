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
