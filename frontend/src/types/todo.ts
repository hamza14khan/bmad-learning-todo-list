// snake_case fields mirror the API response directly — no transform layer
export interface Todo {
  id: number
  text: string
  is_complete: boolean
  created_at: string  // ISO 8601 string, e.g. "2026-03-23T10:00:00Z"
}
