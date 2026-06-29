import {
  BarChart3,
  CalendarClock,
  LayoutDashboard,
  Scissors,
  Users,
  UserRoundCog,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { useLanguage } from '../../context/LanguageContext.jsx'

const navItems = [
  { to: '/', labelKey: 'nav.dashboard', icon: LayoutDashboard, end: true },
  { to: '/services', labelKey: 'nav.services', icon: Scissors },
  { to: '/staff', labelKey: 'nav.staff', icon: UserRoundCog },
  { to: '/bookings', labelKey: 'nav.bookings', icon: CalendarClock },
  { to: '/clients', labelKey: 'nav.clients', icon: Users },
  { to: '/analytics', labelKey: 'nav.analytics', icon: BarChart3 },
]

export function Sidebar() {
  const { t } = useLanguage()

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-[18rem] p-4 lg:block">
      <div className="surface-shell h-full">
        <nav className="surface-core flex h-full flex-col p-4">
          <div className="mb-8 flex items-center gap-3 px-2 pt-1">
            <div className="grid size-11 place-items-center rounded-2xl bg-qabul-ink text-lg font-black text-white shadow-insetline">
              Q
            </div>
            <div>
              <p className="text-lg font-black tracking-[-0.04em]">Qabul</p>
              <p className="text-xs font-medium text-qabul-muted">{t('nav.bookingCrm')}</p>
            </div>
          </div>

          <div className="grid gap-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) =>
                  [
                    'group flex items-center gap-3 rounded-2xl px-3 py-2.5 text-sm font-semibold transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] active:scale-[0.99]',
                    isActive
                      ? 'bg-qabul-leaf text-white shadow-[0_14px_34px_rgba(47,140,103,0.22)]'
                      : 'text-qabul-muted hover:bg-qabul-wash hover:text-qabul-ink',
                  ].join(' ')
                }
              >
                <item.icon size={18} strokeWidth={1.75} />
                <span>{t(item.labelKey)}</span>
              </NavLink>
            ))}
          </div>

          <div className="mt-auto rounded-[1.35rem] bg-qabul-wash p-4 ring-1 ring-qabul-ink/5">
            <p className="text-sm font-bold text-qabul-ink">{t('nav.aiTitle')}</p>
            <p className="mt-1 text-xs leading-5 text-qabul-muted">
              {t('nav.aiText')}
            </p>
          </div>
        </nav>
      </div>
    </aside>
  )
}
