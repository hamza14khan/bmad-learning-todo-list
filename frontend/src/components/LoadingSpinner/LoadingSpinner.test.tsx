import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { LoadingSpinner } from './LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders with role="status" for accessibility', () => {
    render(<LoadingSpinner />)
    expect(screen.getByRole('status')).toBeInTheDocument()
  })

  it('displays loading text', () => {
    render(<LoadingSpinner />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })
})
