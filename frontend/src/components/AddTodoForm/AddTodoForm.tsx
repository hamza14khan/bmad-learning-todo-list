import { useState, useRef } from 'react'
import { useCreateTodo } from '../../hooks/useTodos'
import styles from './AddTodoForm.module.css'

export function AddTodoForm() {
  const [text, setText] = useState('')
  const [validationError, setValidationError] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const { mutate: createTodo, isPending } = useCreateTodo()

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    if (!text.trim()) {
      setValidationError('Please enter a task description.')
      inputRef.current?.focus()
      return
    }
    if (text.length > 200) {
      setValidationError('Task description cannot exceed 200 characters.')
      inputRef.current?.focus()
      return
    }

    setValidationError('')
    createTodo(text.trim(), {
      onSuccess: () => setText(''),
    })
  }

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <input
        ref={inputRef}
        type="text"
        value={text}
        onChange={e => {
          setText(e.target.value)
          setValidationError('')
        }}
        placeholder="Add a new task..."
        className={styles.input}
        aria-label="New todo"
        aria-invalid={validationError ? 'true' : undefined}
        aria-describedby={validationError ? 'todo-form-error' : undefined}
      />
      <button type="submit" disabled={isPending} className={styles.button}>
        {isPending ? 'Adding...' : 'Add'}
      </button>
      {validationError && (
        <p id="todo-form-error" role="alert" className={styles.error}>{validationError}</p>
      )}
    </form>
  )
}
