import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { TodoItem } from './TodoItem'
import * as useTodosModule from '../../hooks/useTodos'

const mockToggle = vi.fn()

beforeEach(() => {
  mockToggle.mockReset()
  vi.spyOn(useTodosModule, 'useToggleTodo').mockReturnValue({
    mutate: mockToggle,
    isPending: false,
  } as any)
})

const activeTodo = { id: 1, text: 'Buy milk', is_complete: false, created_at: '2026-03-23T10:00:00Z' }
const completedTodo = { id: 2, text: 'Walk dog', is_complete: true, created_at: '2026-03-23T11:00:00Z' }

describe('TodoItem', () => {
  it('renders todo text', () => {
    render(<TodoItem todo={activeTodo} />)
    expect(screen.getByText('Buy milk')).toBeInTheDocument()
  })

  it('clicking toggle on active todo calls mutate with is_complete: true', async () => {
    render(<TodoItem todo={activeTodo} />)
    await userEvent.click(screen.getByRole('button'))
    expect(mockToggle).toHaveBeenCalledWith({ id: 1, is_complete: true })
  })

  it('clicking toggle on completed todo calls mutate with is_complete: false', async () => {
    render(<TodoItem todo={completedTodo} />)
    await userEvent.click(screen.getByRole('button'))
    expect(mockToggle).toHaveBeenCalledWith({ id: 2, is_complete: false })
  })

  it('completed todo text has completed CSS class', () => {
    render(<TodoItem todo={completedTodo} />)
    const textSpan = screen.getByText('Walk dog')
    expect(textSpan.className).toMatch(/completed/)
  })

  it('active todo text does not have completed CSS class', () => {
    render(<TodoItem todo={activeTodo} />)
    const textSpan = screen.getByText('Buy milk')
    expect(textSpan.className).not.toMatch(/completed/)
  })
})
