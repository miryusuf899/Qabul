export function FormField({ label, error, children }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      {children}
      {error ? <span className="text-sm font-medium text-red-700">{error}</span> : null}
    </label>
  )
}
