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
import { useLanguage } from '../context/LanguageContext.jsx'
import { formatDate, money, number } from '../utils/format.js'

export function AnalyticsPage() {
  const { selectedBusinessId } = useBusiness()
  const { t } = useLanguage()
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
      <PageHeader title={t('analyticsPage.title')} description={t('analyticsPage.description')} />
      {!selectedBusinessId ? (
        <Panel>
          <EmptyState title={t('analyticsPage.noBusinessTitle')} description={t('analyticsPage.noBusinessText')} />
        </Panel>
      ) : (
        <>
          {error ? <div className="mb-5 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
          <div className="mb-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <StatCard label={t('analyticsPage.week')} value={loading ? '...' : number(summary?.week_bookings)} helper={t('analyticsPage.weekHelper')} />
            <StatCard label={t('analyticsPage.month')} value={loading ? '...' : number(summary?.month_bookings)} helper={t('analyticsPage.monthHelper')} />
            <StatCard label={t('analyticsPage.revenue')} value={loading ? '...' : money(summary?.month_revenue)} helper={t('analyticsPage.revenueHelper')} tone="amber" />
            <StatCard label={t('analyticsPage.cancelled')} value={loading ? '...' : number(summary?.cancelled_bookings_this_month)} helper={t('analyticsPage.cancelledHelper')} />
          </div>
          <div className="grid gap-5 xl:grid-cols-2">
            <Panel>
              <ChartBlock title={t('analyticsPage.bookingsByDay')} data={bookingsByDay} dataKey="value" loading={loading} color="#2f8c67" />
            </Panel>
            <Panel>
              <ChartBlock title={t('analyticsPage.revenueByDay')} data={revenueByDay} dataKey="value" loading={loading} color="#a66f2a" />
            </Panel>
            <Panel>
              <RankList
                title={t('analyticsPage.servicePopularity')}
                rows={charts?.service_popularity || []}
                getLabel={(row) => row.name}
                loading={loading}
              />
            </Panel>
            <Panel>
              <RankList
                title={t('analyticsPage.topStaff')}
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
  const { t } = useLanguage()

  return (
    <>
      <h2 className="mb-4 text-lg font-black tracking-[-0.035em]">{title}</h2>
      {loading ? (
        <div className="skeleton h-72 w-full" />
      ) : data.length === 0 ? (
        <EmptyState title={t('analyticsPage.noChartTitle')} description={t('analyticsPage.noChartText')} />
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
  const { t } = useLanguage()

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
        <EmptyState title={t('analyticsPage.noRankingTitle')} description={t('analyticsPage.noRankingText')} />
      ) : (
        <div className="grid gap-2">
          {rows.map((row, index) => (
            <div
              key={`${getLabel(row)}-${index}`}
              className="flex items-center justify-between rounded-2xl bg-qabul-wash px-4 py-3 ring-1 ring-qabul-ink/5"
            >
              <div>
                <p className="font-semibold text-qabul-ink">{getLabel(row)}</p>
                <p className="text-xs text-qabul-muted">{t('common.rank')} {index + 1}</p>
              </div>
              <span className="font-mono text-sm font-black text-qabul-leaf">{row.count}</span>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
