import type { Todo } from '../types/todo'

// VITE_API_URL comes from frontend/.env — never hardcode localhost:8000
const API_URL = import.meta.env.VITE_API_URL
if (!API_URL) {
  throw new Error('VITE_API_URL is not set. Add VITE_API_URL=http://localhost:8000 to frontend/.env')
}

export async function getTodos(): Promise<Todo[]> {
  const response = await fetch(`${API_URL}/api/v1/todos`)
  if (!response.ok) {
    throw new Error('Unable to load todos. Please try again.')
  }
  return response.json()
}

export async function createTodo(text: string): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/v1/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!response.ok) {
    throw new Error('Unable to create todo. Please try again.')
  }
  return response.json()
}

export async function toggleTodo(id: number, is_complete: boolean): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/v1/todos/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_complete }),
  })
  if (!response.ok) {
    throw new Error('Unable to update todo. Please try again.')
  }
  return response.json()
}

export async function deleteTodo(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/todos/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Unable to delete todo. Please try again.')
  }
}
