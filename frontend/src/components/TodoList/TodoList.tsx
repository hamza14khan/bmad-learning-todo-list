import { LoadingSpinner } from '../LoadingSpinner/LoadingSpinner'
import type { Todo } from '../../types/todo'
import styles from './TodoList.module.css'

interface Props {
  todos: Todo[]
  isLoading: boolean
}

export function TodoList({ todos, isLoading }: Props) {
  if (isLoading) return <LoadingSpinner />

  return (
    <ul className={styles.list}>
      {todos.map(todo => (
        <li key={todo.id} className={styles.item}>
          {todo.text}
        </li>
      ))}
    </ul>
  )
}
