export function AuthFrame({ title, description, children }) {
  return (
    <main className="relative grid min-h-[100dvh] overflow-hidden px-4 py-5 lg:grid-cols-[1.05fr_0.95fr] lg:gap-5 lg:p-5">
      <section className="relative hidden min-h-[calc(100dvh-2.5rem)] overflow-hidden rounded-[2rem] bg-[#121f19] p-7 text-white shadow-[0_28px_110px_rgba(23,33,29,0.24)] lg:flex">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -left-28 top-20 size-96 rounded-full bg-qabul-leaf/25 blur-3xl" />
          <div className="absolute bottom-10 right-0 size-80 rounded-full bg-white/[0.08] blur-3xl" />
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.055)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.045)_1px,transparent_1px)] bg-[size:44px_44px] opacity-60" />
        </div>

        <div className="relative z-10 flex w-full flex-col">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="grid size-12 place-items-center rounded-2xl bg-white text-xl font-black text-qabul-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]">
                Q
              </div>
              <div>
                <p className="text-base font-black tracking-[-0.04em]">Qabul</p>
                <p className="text-xs font-semibold text-white/60">Операционная панель</p>
              </div>
            </div>
            <div className="rounded-full bg-white/[0.08] px-4 py-2 text-xs font-bold text-white/70 ring-1 ring-white/10">
              Live dashboard
            </div>
          </div>

          <div className="mt-12 grid flex-1 gap-8 xl:grid-cols-[0.82fr_1.18fr]">
            <div className="flex flex-col justify-center">
              <h1 className="max-w-xl text-[clamp(3rem,5vw,5.7rem)] font-black leading-[0.86] tracking-[-0.085em]">
                Записи, клиенты и команда в одной спокойной системе.
              </h1>
              <p className="mt-7 max-w-md text-base font-medium leading-7 text-white/66">
                Контролируйте расписание, подтверждайте заявки и держите Telegram-записи рядом с правилами бизнеса.
              </p>

              <div className="mt-10 grid gap-3">
                {[
                  ['Проверка конфликтов', 'Не даёт создать двойную запись в расписании'],
                  ['Telegram заявки', 'Превращает сообщения клиентов в подтверждённые визиты'],
                  ['Аналитика выручки', 'Показывает загрузку, услуги и доход по дням'],
                ].map(([titleText, body]) => (
                  <div
                    key={titleText}
                    className="rounded-[1.25rem] bg-white/[0.075] p-4 ring-1 ring-white/10 transition duration-500 ease-[cubic-bezier(0.32,0.72,0,1)] hover:translate-x-1 hover:bg-white/[0.105]"
                  >
                    <p className="text-sm font-bold">{titleText}</p>
                    <p className="mt-1 text-xs leading-5 text-white/50">{body}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center">
              <div className="w-full rounded-[2rem] bg-white/[0.07] p-2 ring-1 ring-white/10 shadow-[0_32px_90px_rgba(0,0,0,0.22)]">
                <div className="overflow-hidden rounded-[calc(2rem-0.5rem)] bg-[#f8faf6] p-5 text-qabul-ink shadow-[inset_0_1px_0_rgba(255,255,255,0.9)]">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-bold text-qabul-leaf">Сегодня</p>
                      <h2 className="mt-1 text-2xl font-black tracking-[-0.055em]">Barber Pro</h2>
                    </div>
                    <div className="rounded-2xl bg-qabul-leaf px-3 py-2 text-xs font-bold text-white">
                      09:00-20:00
                    </div>
                  </div>

                  <div className="mt-5 grid grid-cols-3 gap-3">
                    {[
                      ['8', 'Записей'],
                      ['580', 'Выручка'],
                      ['3', 'Новых клиента'],
                    ].map(([value, label]) => (
                      <div key={label} className="rounded-2xl bg-white p-4 ring-1 ring-qabul-ink/5">
                        <p className="font-mono text-2xl font-black tracking-[-0.04em]">{value}</p>
                        <p className="mt-1 text-[11px] font-bold text-qabul-muted">{label}</p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-5 rounded-[1.4rem] bg-qabul-ink p-4 text-white">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-bold">Ближайшие записи</p>
                      <span className="rounded-full bg-white/10 px-2.5 py-1 text-[11px] font-bold text-white/70">
                        Telegram AI
                      </span>
                    </div>
                    <div className="mt-4 grid gap-2">
                      {[
                        ['15:00', 'Ali', 'Стрижка'],
                        ['16:30', 'Said', 'Борода'],
                        ['18:00', 'Ali', 'Стрижка + борода'],
                      ].map(([time, master, service]) => (
                        <div key={`${time}-${service}`} className="flex items-center justify-between rounded-2xl bg-white/[0.08] px-3 py-3 ring-1 ring-white/10">
                          <div>
                            <p className="text-sm font-bold">{service}</p>
                            <p className="text-xs text-white/60">Мастер {master}</p>
                          </div>
                          <span className="font-mono text-xs font-bold text-white/72">{time}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-5 h-24 rounded-[1.4rem] bg-[linear-gradient(135deg,rgba(47,140,103,0.22),rgba(166,111,42,0.12))] p-4 ring-1 ring-qabul-ink/5">
                    <div className="flex h-full items-end gap-2">
                      {[32, 54, 42, 78, 58, 88, 72, 96].map((height, index) => (
                        <div
                          key={index}
                          className="flex-1 rounded-t-xl bg-qabul-leaf"
                          style={{ height: `${height}%`, opacity: 0.38 + index * 0.055 }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid place-items-center py-6 lg:py-0">
        <div className="surface-shell w-full max-w-[28rem] rounded-[2rem]">
          <div className="surface-core rounded-[calc(2rem-0.375rem)] p-6 sm:p-8">
            <div className="mb-6">
              <div className="mb-7 flex items-center justify-between">
                <div className="grid size-11 place-items-center rounded-2xl bg-qabul-ink text-lg font-black text-white">
                  Q
                </div>
                <span className="rounded-full bg-qabul-wash px-3 py-1.5 text-xs font-bold text-qabul-muted">
                  Доступ владельца
                </span>
              </div>
              <h1 className="text-3xl font-black tracking-[-0.065em] text-qabul-ink">{title}</h1>
              <p className="mt-3 text-sm font-medium leading-6 text-qabul-muted">{description}</p>
            </div>
            {children}
          </div>
        </div>
      </section>
    </main>
  )
}
