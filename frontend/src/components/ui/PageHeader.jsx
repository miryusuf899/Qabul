export function PageHeader({ title, description, action }) {
  return (
    <div data-gsap="fade-up" className="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <h1 className="max-w-3xl text-3xl font-black tracking-[-0.055em] text-qabul-ink md:text-4xl">
          {title}
        </h1>
        {description ? <p className="mt-2 max-w-2xl text-sm leading-6 text-qabul-muted">{description}</p> : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  )
}
