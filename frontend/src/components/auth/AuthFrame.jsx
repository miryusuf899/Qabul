export function AuthFrame({ title, description, children }) {
  return (
    <main className="grid min-h-[100dvh] px-4 py-6 lg:grid-cols-[0.95fr_1.05fr] lg:gap-6 lg:p-6">
      <section className="hidden min-h-[calc(100dvh-3rem)] rounded-[2rem] bg-qabul-ink p-8 text-white shadow-[0_24px_90px_rgba(23,33,29,0.22)] lg:flex">
        <div className="flex w-full flex-col justify-between">
          <div>
            <div className="grid size-12 place-items-center rounded-2xl bg-white text-xl font-black text-qabul-ink">
              Q
            </div>
            <h1 className="mt-10 max-w-xl text-5xl font-black leading-[0.95] tracking-[-0.07em]">
              Qabul keeps bookings under control.
            </h1>
            <p className="mt-5 max-w-md text-base leading-7 text-white/68">
              Manage services, masters, clients and Telegram requests from one operational dashboard.
            </p>
          </div>
          <div className="grid gap-3 xl:grid-cols-3">
            {['Conflict checks', 'Telegram intake', 'Revenue analytics'].map((item) => (
              <div key={item} className="rounded-2xl bg-white/[0.08] p-4 text-sm font-semibold ring-1 ring-white/10">
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="grid place-items-center py-6">
        <div className="surface-shell w-full max-w-md">
          <div className="surface-core p-6 sm:p-7">
            <div className="mb-6">
              <p className="text-sm font-semibold text-qabul-leaf">Qabul</p>
              <h1 className="mt-2 text-3xl font-black tracking-[-0.055em]">{title}</h1>
              <p className="mt-2 text-sm leading-6 text-qabul-muted">{description}</p>
            </div>
            {children}
          </div>
        </div>
      </section>
    </main>
  )
}
