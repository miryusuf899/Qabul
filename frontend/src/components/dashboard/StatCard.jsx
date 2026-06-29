export function StatCard({ label, value, helper, tone = 'green' }) {
  const toneClass = tone === 'amber' ? 'text-qabul-amber bg-qabul-amber/[0.12]' : 'text-qabul-leaf bg-qabul-leaf/10'

  return (
    <div data-gsap="card" className="surface-shell premium-card stat-card">
      <div className="surface-core p-5">
        <div className={`mb-5 inline-flex rounded-xl px-2.5 py-1 text-xs font-bold ${toneClass}`}>{label}</div>
        <p className="font-mono text-3xl font-black tracking-[-0.05em] text-qabul-ink">{value}</p>
        {helper ? <p className="mt-2 text-sm leading-5 text-qabul-muted">{helper}</p> : null}
      </div>
    </div>
  )
}
