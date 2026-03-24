import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AddTodoForm } from './AddTodoForm'
import * as useTodosModule from '../../hooks/useTodos'

const mockMutate = vi.fn()

beforeEach(() => {
  mockMutate.mockReset()
  vi.spyOn(useTodosModule, 'useCreateTodo').mockReturnValue({
    mutate: mockMutate,
    isPending: false,
  } as any)
})

describe('AddTodoForm', () => {
  it('renders input and Add button', () => {
    render(<AddTodoForm />)
    expect(screen.getByRole('textbox', { name: /new todo/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add/i })).toBeInTheDocument()
  })

  it('shows validation error on empty submit', async () => {
    render(<AddTodoForm />)
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('shows validation error on whitespace-only submit', async () => {
    render(<AddTodoForm />)
    await userEvent.type(screen.getByRole('textbox'), '   ')
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('shows validation error when text exceeds 200 characters', async () => {
    render(<AddTodoForm />)
    await userEvent.type(screen.getByRole('textbox'), 'x'.repeat(201))
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(mockMutate).not.toHaveBeenCalled()
  })

  it('input has aria-invalid when validation error is shown', async () => {
    render(<AddTodoForm />)
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    const input = screen.getByRole('textbox', { name: /new todo/i })
    expect(input).toHaveAttribute('aria-invalid', 'true')
  })

  it('input has aria-describedby pointing to error element when error is shown', async () => {
    render(<AddTodoForm />)
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    const input = screen.getByRole('textbox', { name: /new todo/i })
    expect(input).toHaveAttribute('aria-describedby', 'todo-form-error')
    expect(document.getElementById('todo-form-error')).toBeInTheDocument()
  })

  it('clears input after successful submission', async () => {
    mockMutate.mockImplementation((_text: string, options: any) => {
      options?.onSuccess?.()
    })
    render(<AddTodoForm />)
    await userEvent.type(screen.getByRole('textbox'), 'Buy milk')
    await userEvent.click(screen.getByRole('button', { name: /add/i }))
    expect(screen.getByRole('textbox')).toHaveValue('')
  })
})
