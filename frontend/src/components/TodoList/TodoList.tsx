import { LoadingSpinner } from '../LoadingSpinner/LoadingSpinner'
import { TodoItem } from '../TodoItem/TodoItem'
import type { Todo } from '../../types/todo'
import styles from './TodoList.module.css'

interface Props {
  todos: Todo[]
  isLoading: boolean
}

export function TodoList({ todos, isLoading }: Props) {
  if (isLoading) return <LoadingSpinner />

  if (todos.length === 0) {
    return <p className={styles.empty}>No todos yet. Add your first task!</p>
  }

  return (
    <ul className={styles.list}>
      {todos.map(todo => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
    </ul>
  )
}
