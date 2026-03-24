import { useGetTodos } from './hooks/useTodos'
import { AddTodoForm } from './components/AddTodoForm/AddTodoForm'
import { TodoList } from './components/TodoList/TodoList'
import { ErrorMessage } from './components/ErrorMessage/ErrorMessage'
import './App.css'

export default function App() {
  const { data: todos = [], isLoading, isError } = useGetTodos()

  return (
    <main className="app">
      <h1>Todo List</h1>
      <AddTodoForm />
      {isError ? (
        <ErrorMessage />
      ) : (
        <TodoList todos={todos} isLoading={isLoading} />
      )}
    </main>
  )
}
