import styles from './LoadingSpinner.module.css'

export function LoadingSpinner() {
  return (
    <div role="status" className={styles.spinner}>
      Loading...
    </div>
  )
}
