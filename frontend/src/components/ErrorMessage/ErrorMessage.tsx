import styles from './ErrorMessage.module.css'

interface Props {
  message?: string
}

export function ErrorMessage({ message }: Props) {
  return (
    <div role="alert" className={styles.error}>
      <p>Something went wrong. Please check the backend connection.</p>
      {message && <p className={styles.detail}>{message}</p>}
    </div>
  )
}
