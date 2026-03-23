import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTodos, createTodo, toggleTodo, deleteTodo } from '../api/todos'
import type { Todo } from '../types/todo'

export function useGetTodos() {
  return useQuery<Todo[]>({
    queryKey: ['todos'],
    queryFn: getTodos,
  })
}

export function useCreateTodo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (text: string) => createTodo(text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}

export function useToggleTodo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, is_complete }: { id: number; is_complete: boolean }) =>
      toggleTodo(id, is_complete),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}

export function useDeleteTodo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteTodo(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}
