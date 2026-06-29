import { Bell, ChevronDown, LogOut, Search } from 'lucide-react'

import { useAuth } from '../../context/AuthContext.jsx'
import { useBusiness } from '../../context/BusinessContext.jsx'
import { useLanguage } from '../../context/LanguageContext.jsx'
import { LanguageSwitcher } from './LanguageSwitcher.jsx'

export function Navbar() {
  const { user, logout } = useAuth()
  const { businesses, selectedBusinessId, setSelectedBusinessId, loading } = useBusiness()
  const { t } = useLanguage()

  return (
    <header className="sticky top-0 z-30 border-b border-qabul-ink/5 bg-qabul-mist/[0.82] px-4 py-3 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-[1480px] items-center gap-3">
        <div className="hidden flex-1 items-center rounded-full bg-white px-3 py-2 ring-1 ring-qabul-ink/[0.08] md:flex">
          <Search size={17} strokeWidth={1.7} className="text-qabul-muted" />
          <input
            className="h-7 flex-1 bg-transparent px-2 text-sm outline-none placeholder:text-qabul-muted/70"
            placeholder={t('nav.search')}
            type="search"
          />
        </div>

        <div className="ml-auto flex items-center gap-2">
          <label className="sr-only" htmlFor="business-select">
            {t('nav.business')}
          </label>
          <div className="relative">
            <select
              id="business-select"
              className="h-10 min-w-40 appearance-none rounded-full bg-white pl-4 pr-9 text-sm font-semibold text-qabul-ink ring-1 ring-qabul-ink/[0.08] transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] focus:outline-none focus:ring-2 focus:ring-qabul-leaf/25"
              value={selectedBusinessId || ''}
              disabled={loading || businesses.length === 0}
              onChange={(event) => setSelectedBusinessId(Number(event.target.value))}
            >
              {businesses.length === 0 ? <option value="">{t('nav.noBusiness')}</option> : null}
              {businesses.map((business) => (
                <option key={business.id} value={business.id}>
                  {business.name}
                </option>
              ))}
            </select>
            <ChevronDown
              size={16}
              strokeWidth={1.8}
              className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-qabul-muted"
            />
          </div>

          <LanguageSwitcher compact />

          <button className="btn btn-secondary size-10 p-0" aria-label={t('nav.notifications')}>
            <Bell size={17} strokeWidth={1.8} />
          </button>
          <div className="hidden min-w-0 flex-col px-2 text-right sm:flex">
            <span className="truncate text-sm font-semibold">{user?.full_name || t('nav.owner')}</span>
            <span className="truncate text-xs text-qabul-muted">{user?.email}</span>
          </div>
          <button className="btn btn-secondary size-10 p-0" onClick={logout} aria-label={t('nav.logout')}>
            <LogOut size={17} strokeWidth={1.8} />
          </button>
        </div>
      </div>
    </header>
  )
}
