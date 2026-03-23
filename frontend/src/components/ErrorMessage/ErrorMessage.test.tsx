import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ErrorMessage } from './ErrorMessage'

describe('ErrorMessage', () => {
  it('renders alert role', () => {
    render(<ErrorMessage />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })

  it('shows detail message when provided', () => {
    render(<ErrorMessage message="Failed to fetch todos: 503" />)
    expect(screen.getByText('Failed to fetch todos: 503')).toBeInTheDocument()
  })

  it('renders without message prop', () => {
    render(<ErrorMessage />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.queryByText(/failed/i)).not.toBeInTheDocument()
  })
})
