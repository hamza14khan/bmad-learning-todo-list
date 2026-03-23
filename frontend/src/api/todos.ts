import type { Todo } from '../types/todo'

// VITE_API_URL comes from frontend/.env — never hardcode localhost:8000
const API_URL = import.meta.env.VITE_API_URL

export async function getTodos(): Promise<Todo[]> {
  const response = await fetch(`${API_URL}/api/v1/todos`)
  if (!response.ok) {
    throw new Error(`Failed to fetch todos: ${response.status}`)
  }
  return response.json()
}
