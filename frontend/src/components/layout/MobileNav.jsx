import {
  BarChart3,
  CalendarClock,
  LayoutDashboard,
  Scissors,
  Users,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

import { useLanguage } from '../../context/LanguageContext.jsx'

const mobileItems = [
  { to: '/', labelKey: 'nav.dashboard', icon: LayoutDashboard, end: true },
  { to: '/services', labelKey: 'nav.services', icon: Scissors },
  { to: '/bookings', labelKey: 'nav.bookings', icon: CalendarClock },
  { to: '/clients', labelKey: 'nav.clients', icon: Users },
  { to: '/analytics', labelKey: 'nav.analytics', icon: BarChart3 },
]

export function MobileNav() {
  const { t } = useLanguage()

  return (
    <nav className="fixed inset-x-3 bottom-3 z-40 rounded-[1.4rem] bg-qabul-ink/92 p-1.5 shadow-[0_18px_60px_rgba(23,33,29,0.24)] backdrop-blur-xl lg:hidden">
      <div className="grid grid-cols-5 gap-1">
        {mobileItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              [
                'flex min-h-14 flex-col items-center justify-center gap-1 rounded-[1.05rem] text-[11px] font-semibold transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] active:scale-[0.98]',
                isActive ? 'bg-white text-qabul-ink' : 'text-white/70 hover:bg-white/10 hover:text-white',
              ].join(' ')
            }
          >
            <item.icon size={18} strokeWidth={1.65} />
            <span>{t(item.labelKey)}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
