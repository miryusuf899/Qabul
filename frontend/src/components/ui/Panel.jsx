export function Panel({ children, className = '' }) {
  return (
    <div data-scroll-reveal className={`surface-shell premium-card ${className}`}>
      <div className="surface-core h-full p-5">{children}</div>
    </div>
  )
}
