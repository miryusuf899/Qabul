import { Badge } from '../ui/Badge.jsx'
import { EmptyState } from '../ui/EmptyState.jsx'
import { formatDateTime, money } from '../../utils/format.js'
import { useLanguage } from '../../context/LanguageContext.jsx'

const statusTone = {
  pending: 'amber',
  confirmed: 'green',
  completed: 'graphite',
  cancelled: 'red',
  no_show: 'red',
}

export function UpcomingBookings({ bookings, loading }) {
  const { t } = useLanguage()

  if (loading) {
    return (
      <div className="grid gap-3">
        <div className="skeleton h-16" />
        <div className="skeleton h-16" />
        <div className="skeleton h-16" />
      </div>
    )
  }

  if (!bookings.length) {
    return (
      <EmptyState
        title={t('upcoming.emptyTitle')}
        description={t('upcoming.emptyText')}
      />
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl ring-1 ring-qabul-ink/5">
      <table className="w-full border-collapse bg-white">
        <thead className="bg-qabul-wash">
          <tr>
            <th className="table-th">{t('common.client')}</th>
            <th className="table-th">{t('common.service')}</th>
            <th className="table-th">{t('common.time')}</th>
            <th className="table-th">{t('common.status')}</th>
          </tr>
        </thead>
        <tbody>
          {bookings.map((booking) => (
            <tr key={booking.id} className="transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-qabul-wash/70">
              <td className="table-td">
                <div className="font-semibold text-qabul-ink">{booking.client_name || t('common.client')}</div>
                <div className="text-xs text-qabul-muted">{booking.client_phone || t('common.noPhone')}</div>
              </td>
              <td className="table-td">
                <div className="font-semibold text-qabul-ink">{booking.service_name}</div>
                <div className="text-xs text-qabul-muted">{money(booking.service_price)}</div>
              </td>
              <td className="table-td font-mono text-xs">{formatDateTime(booking.start_time)}</td>
              <td className="table-td">
                <Badge tone={statusTone[booking.status] || 'graphite'}>{t(`status.${booking.status}`)}</Badge>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
