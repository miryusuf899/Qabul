export function PageLoader({ label = 'Загружаем данные' }) {
  return (
    <div className="grid min-h-[100dvh] place-items-center px-4">
      <div className="surface-shell w-full max-w-sm">
        <div className="surface-core p-6">
          <div className="skeleton h-3 w-24" />
          <div className="skeleton mt-5 h-10 w-full" />
          <p className="mt-4 text-sm font-semibold text-qabul-muted">{label}</p>
        </div>
      </div>
    </div>
  )
}
