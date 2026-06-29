export function EmptyState({ title, description, action }) {
  return (
    <div className="rounded-[1.5rem] bg-qabul-wash px-6 py-10 text-center ring-1 ring-qabul-ink/5">
      <h3 className="text-lg font-black tracking-[-0.03em] text-qabul-ink">{title}</h3>
      <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-qabul-muted">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  )
}
