export function Panel({ children, className = '' }) {
  return (
    <div className={`surface-shell ${className}`}>
      <div className="surface-core h-full p-5">{children}</div>
    </div>
  )
}
