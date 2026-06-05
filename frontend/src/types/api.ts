/** Generic paginated response used by list endpoints */
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}
