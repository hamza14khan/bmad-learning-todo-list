import { useToggleTodo, useDeleteTodo } from '../../hooks/useTodos'
import type { Todo } from '../../types/todo'
import styles from './TodoItem.module.css'

interface Props {
  todo: Todo
}

export function TodoItem({ todo }: Props) {
  const { mutate: toggleTodo } = useToggleTodo()
  const { mutate: deleteTodo } = useDeleteTodo()

  return (
    <li className={styles.item}>
      <button
        className={styles.toggle}
        onClick={() => toggleTodo({ id: todo.id, is_complete: !todo.is_complete })}
        aria-label={todo.is_complete ? 'Mark as active' : 'Mark as complete'}
      >
        {todo.is_complete ? '✓' : '○'}
      </button>
      <span className={`${styles.text} ${todo.is_complete ? styles.completed : ''}`}>
        {todo.text}
      </span>
      <button
        className={styles.delete}
        onClick={() => deleteTodo(todo.id)}
        aria-label="Delete todo"
      >
        ✕
      </button>
    </li>
  )
}
