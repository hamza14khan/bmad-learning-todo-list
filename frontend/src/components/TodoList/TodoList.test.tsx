import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { TodoList } from './TodoList'
import * as useTodosModule from '../../hooks/useTodos'

beforeEach(() => {
  vi.spyOn(useTodosModule, 'useToggleTodo').mockReturnValue({
    mutate: vi.fn(),
    isPending: false,
  } as any)
  vi.spyOn(useTodosModule, 'useDeleteTodo').mockReturnValue({
    mutate: vi.fn(),
    isPending: false,
  } as any)
})

const mockTodos = [
  { id: 1, text: 'Buy milk', is_complete: false, created_at: '2026-03-23T10:00:00Z' },
  { id: 2, text: 'Walk dog', is_complete: true, created_at: '2026-03-23T11:00:00Z' },
]

describe('TodoList', () => {
  it('shows loading spinner when isLoading is true', () => {
    render(<TodoList todos={[]} isLoading={true} />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('renders todo items when data is loaded', () => {
    render(<TodoList todos={mockTodos} isLoading={false} />)
    expect(screen.getByText('Buy milk')).toBeInTheDocument()
    expect(screen.getByText('Walk dog')).toBeInTheDocument()
  })

  it('shows empty state message when todos is [] and not loading', () => {
    render(<TodoList todos={[]} isLoading={false} />)
    expect(screen.getByText(/add your first task/i)).toBeInTheDocument()
    expect(screen.queryByRole('list')).not.toBeInTheDocument()
  })
})
