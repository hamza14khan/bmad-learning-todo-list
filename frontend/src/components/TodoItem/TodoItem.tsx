import { useToggleTodo } from '../../hooks/useTodos'
import type { Todo } from '../../types/todo'
import styles from './TodoItem.module.css'

interface Props {
  todo: Todo
}

export function TodoItem({ todo }: Props) {
  const { mutate: toggleTodo } = useToggleTodo()

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
    </li>
  )
}
