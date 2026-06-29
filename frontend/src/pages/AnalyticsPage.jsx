import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { api, getErrorMessage } from '../api/client.js'
import { StatCard } from '../components/dashboard/StatCard.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'
import { formatDate, money, number } from '../utils/format.js'

export function AnalyticsPage() {
  const { selectedBusinessId } = useBusiness()
  const [summary, setSummary] = useState(null)
  const [charts, setCharts] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    async function loadAnalytics() {
      if (!selectedBusinessId) return
      setLoading(true)
      setError('')
      try {
        const [summaryResponse, chartsResponse] = await Promise.all([
          api.get(`/businesses/${selectedBusinessId}/dashboard/summary`),
          api.get(`/businesses/${selectedBusinessId}/dashboard/charts`),
        ])
        if (cancelled) return
        setSummary(summaryResponse.data)
        setCharts(chartsResponse.data)
      } catch (requestError) {
        if (!cancelled) setError(getErrorMessage(requestError, 'Не удалось загрузить аналитику'))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadAnalytics()
    return () => {
      cancelled = true
    }
  }, [selectedBusinessId])

  const bookingsByDay = charts?.bookings_by_day?.map((item) => ({
    ...item,
    label: formatDate(item.date),
  })) || []

  const revenueByDay = charts?.revenue_by_day?.map((item) => ({
    ...item,
    label: formatDate(item.date),
  })) || []

  return (
    <>
      <PageHeader title="Analytics" description="Revenue, bookings and service performance in one place." />
      {!selectedBusinessId ? (
        <Panel>
          <EmptyState title="No business selected" description="Select a business before opening analytics." />
        </Panel>
      ) : (
        <>
          {error ? <div className="mb-5 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
          <div className="mb-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Week" value={loading ? '...' : number(summary?.week_bookings)} helper="Bookings this week" />
            <StatCard label="Month" value={loading ? '...' : number(summary?.month_bookings)} helper="Bookings this month" />
            <StatCard label="Revenue" value={loading ? '...' : money(summary?.month_revenue)} helper="Monthly revenue" tone="amber" />
            <StatCard label="Cancelled" value={loading ? '...' : number(summary?.cancelled_bookings_this_month)} helper="This month" />
          </div>
          <div className="grid gap-5 xl:grid-cols-2">
            <Panel>
              <ChartBlock title="Bookings by day" data={bookingsByDay} dataKey="value" loading={loading} color="#2f8c67" />
            </Panel>
            <Panel>
              <ChartBlock title="Revenue by day" data={revenueByDay} dataKey="value" loading={loading} color="#a66f2a" />
            </Panel>
            <Panel>
              <RankList
                title="Service popularity"
                rows={charts?.service_popularity || []}
                getLabel={(row) => row.name}
                loading={loading}
              />
            </Panel>
            <Panel>
              <RankList
                title="Top staff"
                rows={charts?.top_staff || []}
                getLabel={(row) => row.full_name}
                loading={loading}
              />
            </Panel>
          </div>
        </>
      )}
    </>
  )
}

function ChartBlock({ title, data, dataKey, color, loading }) {
  return (
    <>
      <h2 className="mb-4 text-lg font-black tracking-[-0.035em]">{title}</h2>
      {loading ? (
        <div className="skeleton h-72 w-full" />
      ) : data.length === 0 ? (
        <EmptyState title="No chart data" description="Create bookings to populate this chart." />
      ) : (
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid stroke="rgba(23,33,29,0.08)" vertical={false} />
              <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fill: '#65736c', fontSize: 12 }} />
              <YAxis tickLine={false} axisLine={false} tick={{ fill: '#65736c', fontSize: 12 }} width={42} />
              <Tooltip
                contentStyle={{
                  border: '0',
                  borderRadius: '16px',
                  boxShadow: '0 18px 60px rgba(38, 48, 43, 0.12)',
                }}
              />
              <Bar dataKey={dataKey} fill={color} radius={[12, 12, 6, 6]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </>
  )
}

function RankList({ title, rows, getLabel, loading }) {
  return (
    <>
      <h2 className="mb-4 text-lg font-black tracking-[-0.035em]">{title}</h2>
      {loading ? (
        <div className="grid gap-3">
          <div className="skeleton h-14" />
          <div className="skeleton h-14" />
          <div className="skeleton h-14" />
        </div>
      ) : rows.length === 0 ? (
        <EmptyState title="No ranking yet" description="Completed and confirmed bookings will build this list." />
      ) : (
        <div className="grid gap-2">
          {rows.map((row, index) => (
            <div
              key={`${getLabel(row)}-${index}`}
              className="flex items-center justify-between rounded-2xl bg-qabul-wash px-4 py-3 ring-1 ring-qabul-ink/5"
            >
              <div>
                <p className="font-semibold text-qabul-ink">{getLabel(row)}</p>
                <p className="text-xs text-qabul-muted">Rank {index + 1}</p>
              </div>
              <span className="font-mono text-sm font-black text-qabul-leaf">{row.count}</span>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
