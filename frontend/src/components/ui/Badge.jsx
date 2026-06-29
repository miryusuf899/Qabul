const toneClass = {
  green: 'bg-qabul-leaf/10 text-qabul-leaf',
  amber: 'bg-qabul-amber/[0.12] text-qabul-amber',
  graphite: 'bg-qabul-ink/[0.08] text-qabul-graphite',
  red: 'bg-red-50 text-red-700',
}

export function Badge({ children, tone = 'graphite' }) {
  return (
    <span className={`inline-flex items-center rounded-lg px-2 py-1 text-xs font-semibold ${toneClass[tone]}`}>
      {children}
    </span>
  )
}
