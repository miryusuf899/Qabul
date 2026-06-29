import { useEffect, useState } from 'react'
import { CalendarClock, Plus, Store } from 'lucide-react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { api, getErrorMessage } from '../api/client.js'
import { BusinessCreateForm } from '../components/business/BusinessCreateForm.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { StatCard } from '../components/dashboard/StatCard.jsx'
import { UpcomingBookings } from '../components/dashboard/UpcomingBookings.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'
import { formatDate, money, number } from '../utils/format.js'

export function DashboardPage() {
  const { selectedBusiness, selectedBusinessId, loading: businessLoading } = useBusiness()
  const [summary, setSummary] = useState(null)
  const [charts, setCharts] = useState(null)
  const [bookings, setBookings] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    async function loadDashboard() {
      if (!selectedBusinessId) return
      setLoading(true)
      setError('')
      try {
        const [summaryResponse, chartsResponse, bookingsResponse] = await Promise.all([
          api.get(`/businesses/${selectedBusinessId}/dashboard/summary`),
          api.get(`/businesses/${selectedBusinessId}/dashboard/charts`),
          api.get(`/businesses/${selectedBusinessId}/bookings`),
        ])
        if (cancelled) return
        setSummary(summaryResponse.data)
        setCharts(chartsResponse.data)
        setBookings(bookingsResponse.data.slice(0, 6))
      } catch (requestError) {
        if (!cancelled) setError(getErrorMessage(requestError, 'Не удалось загрузить dashboard'))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadDashboard()
    return () => {
      cancelled = true
    }
  }, [selectedBusinessId])

  if (!businessLoading && !selectedBusinessId) {
    return (
      <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div>
          <PageHeader
            title="Create your first business"
            description="Qabul needs a business profile before services, staff and bookings can be managed."
          />
          <Panel>
            <BusinessCreateForm />
          </Panel>
        </div>
        <Panel className="xl:mt-16">
          <div className="flex h-full min-h-80 flex-col justify-between">
            <div>
              <div className="grid size-12 place-items-center rounded-2xl bg-qabul-leaf/10 text-qabul-leaf">
                <Store size={23} strokeWidth={1.7} />
              </div>
              <h2 className="mt-6 text-2xl font-black tracking-[-0.05em]">Built for daily operations</h2>
              <p className="mt-3 max-w-lg text-sm leading-6 text-qabul-muted">
                Add services, connect staff, set working hours and let Telegram clients request bookings.
              </p>
            </div>
            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              {['Services', 'Staff', 'Bookings'].map((item) => (
                <div key={item} className="rounded-2xl bg-qabul-wash p-4 text-sm font-bold text-qabul-ink ring-1 ring-qabul-ink/5">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </Panel>
      </div>
    )
  }

  return (
    <>
      <PageHeader
        title={selectedBusiness ? `${selectedBusiness.name} dashboard` : 'Dashboard'}
        description="Bookings, revenue, clients and upcoming work for the selected business."
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            New booking
          </button>
        }
      />
      {error ? <div className="mb-5 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
      <div className="mb-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Today"
          value={loading ? '...' : number(summary?.today_bookings)}
          helper="Bookings today"
        />
        <StatCard
          label="Month"
          value={loading ? '...' : number(summary?.month_bookings)}
          helper="Bookings this month"
        />
        <StatCard
          label="Revenue"
          value={loading ? '...' : money(summary?.month_revenue)}
          helper="Confirmed and completed"
          tone="amber"
        />
        <StatCard
          label="Clients"
          value={loading ? '...' : number(summary?.new_clients_this_month)}
          helper="New this month"
        />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.35fr_0.65fr]">
        <Panel>
          <div className="mb-4 flex items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-black tracking-[-0.035em]">Bookings and revenue</h2>
              <p className="text-sm text-qabul-muted">Last 14 days</p>
            </div>
          </div>
          {loading ? (
            <div className="skeleton h-80 w-full" />
          ) : charts?.bookings_by_day?.length ? (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={charts.bookings_by_day.map((item) => ({ ...item, label: formatDate(item.date) }))}>
                  <defs>
                    <linearGradient id="bookingsFill" x1="0" x2="0" y1="0" y2="1">
                      <stop offset="0%" stopColor="#2f8c67" stopOpacity={0.28} />
                      <stop offset="100%" stopColor="#2f8c67" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="rgba(23,33,29,0.08)" vertical={false} />
                  <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: '#65736c', fontSize: 12 }} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: '#65736c', fontSize: 12 }} width={32} />
                  <Tooltip
                    contentStyle={{
                      border: '0',
                      borderRadius: '16px',
                      boxShadow: '0 18px 60px rgba(38, 48, 43, 0.12)',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#2f8c67"
                    strokeWidth={2}
                    fill="url(#bookingsFill)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState title="No chart data yet" description="Bookings will start shaping the chart once appointments exist." />
          )}
        </Panel>
        <Panel>
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-black tracking-[-0.035em]">Upcoming bookings</h2>
              <p className="text-sm text-qabul-muted">Nearest appointments</p>
            </div>
            <CalendarClock size={19} strokeWidth={1.7} className="text-qabul-muted" />
          </div>
          <UpcomingBookings bookings={bookings} loading={loading} />
        </Panel>
      </div>
    </>
  )
}
