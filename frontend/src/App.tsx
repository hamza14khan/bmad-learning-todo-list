import { useGetTodos } from './hooks/useTodos'
import { TodoList } from './components/TodoList/TodoList'
import './App.css'

export default function App() {
  const { data: todos = [], isLoading } = useGetTodos()

  return (
    <main className="app">
      <h1>Todo List</h1>
      <TodoList todos={todos} isLoading={isLoading} />
    </main>
  )
}
