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

export async function createTodo(text: string): Promise<Todo> {
  const response = await fetch(`${API_URL}/api/v1/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  if (!response.ok) {
    throw new Error(`Failed to create todo: ${response.status}`)
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
    throw new Error(`Failed to update todo: ${response.status}`)
  }
  return response.json()
}

export async function deleteTodo(id: number): Promise<void> {
  const response = await fetch(`${API_URL}/api/v1/todos/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error(`Failed to delete todo: ${response.status}`)
  }
}
