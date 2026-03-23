import { useQuery } from '@tanstack/react-query'
import { getTodos } from '../api/todos'
import type { Todo } from '../types/todo'

export function useGetTodos() {
  return useQuery<Todo[]>({
    queryKey: ['todos'],  // cache key — Epic 2 mutations will invalidate this
    queryFn: getTodos,
  })
}
