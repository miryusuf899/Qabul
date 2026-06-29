import { useEffect, useMemo, useState } from 'react'
import { Ban, CheckCircle2, Plus, RefreshCcw } from 'lucide-react'

import { api, getErrorMessage } from '../api/client.js'
import { Badge } from '../components/ui/Badge.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { FormField } from '../components/ui/FormField.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'
import { useLanguage } from '../context/LanguageContext.jsx'
import { formatDateTime, money } from '../utils/format.js'

const emptyForm = {
  client_name: '',
  client_phone: '',
  staff_id: '',
  service_id: '',
  start_time: '',
  note: '',
}

const statusTone = {
  pending: 'amber',
  confirmed: 'green',
  completed: 'graphite',
  cancelled: 'red',
  no_show: 'red',
}

export function BookingsPage() {
  const { selectedBusinessId } = useBusiness()
  const { t } = useLanguage()
  const [bookings, setBookings] = useState([])
  const [services, setServices] = useState([])
  const [staff, setStaff] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [filters, setFilters] = useState({ date: '', status: '', staff_id: '', service_id: '' })
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const activeServices = useMemo(() => services.filter((service) => service.is_active), [services])
  const activeStaff = useMemo(() => staff.filter((member) => member.is_active), [staff])

  async function loadBaseData() {
    if (!selectedBusinessId) return
    setLoading(true)
    setError('')
    try {
      const [servicesResponse, staffResponse] = await Promise.all([
        api.get(`/businesses/${selectedBusinessId}/services`),
        api.get(`/businesses/${selectedBusinessId}/staff`),
      ])
      setServices(servicesResponse.data)
      setStaff(staffResponse.data)
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось загрузить данные для записей'))
    } finally {
      setLoading(false)
    }
  }

  async function loadBookings() {
    if (!selectedBusinessId) return
    setLoading(true)
    setError('')
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value)
    })
    try {
      const { data } = await api.get(`/businesses/${selectedBusinessId}/bookings?${params.toString()}`)
      setBookings(data)
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось загрузить записи'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadBaseData()
  }, [selectedBusinessId])

  useEffect(() => {
    loadBookings()
  }, [selectedBusinessId, filters])

  async function handleSubmit(event) {
    event.preventDefault()
    if (!selectedBusinessId) return
    setSubmitting(true)
    setError('')
    try {
      await api.post(`/businesses/${selectedBusinessId}/bookings`, {
        client_name: form.client_name || null,
        client_phone: form.client_phone || null,
        staff_id: Number(form.staff_id),
        service_id: Number(form.service_id),
        start_time: form.start_time,
        note: form.note || null,
      })
      setForm(emptyForm)
      await loadBookings()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось создать запись'))
    } finally {
      setSubmitting(false)
    }
  }

  async function changeStatus(bookingId, status) {
    setError('')
    try {
      await api.patch(`/bookings/${bookingId}/status`, { status })
      await loadBookings()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось изменить статус'))
    }
  }

  async function cancelBooking(bookingId) {
    setError('')
    try {
      await api.delete(`/bookings/${bookingId}`, { params: { reason: t('bookingsPage.cancelReason') } })
      await loadBookings()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось отменить запись'))
    }
  }

  return (
    <>
      <PageHeader
        title={t('bookingsPage.title')}
        description={t('bookingsPage.description')}
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            {t('bookingsPage.newAction')}
          </button>
        }
      />
      {!selectedBusinessId ? (
        <Panel>
          <EmptyState title={t('bookingsPage.noBusinessTitle')} description={t('bookingsPage.noBusinessText')} />
        </Panel>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
          <Panel>
            <h2 className="text-lg font-black tracking-[-0.035em]">{t('bookingsPage.createTitle')}</h2>
            <p className="mt-1 text-sm leading-6 text-qabul-muted">
              {t('bookingsPage.formText')}
            </p>
            <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
              {error ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
              <FormField label={t('bookingsPage.clientName')}>
                <input
                  className="input"
                  value={form.client_name}
                  onChange={(event) => setForm({ ...form, client_name: event.target.value })}
                />
              </FormField>
              <FormField label={t('bookingsPage.clientPhone')}>
                <input
                  className="input"
                  value={form.client_phone}
                  onChange={(event) => setForm({ ...form, client_phone: event.target.value })}
                />
              </FormField>
              <FormField label={t('common.service')}>
                <select
                  className="select"
                  required
                  value={form.service_id}
                  onChange={(event) => setForm({ ...form, service_id: event.target.value })}
                >
                  <option value="">{t('bookingsPage.selectService')}</option>
                  {activeServices.map((service) => (
                    <option key={service.id} value={service.id}>
                      {service.name} - {service.duration_minutes} {t('common.minutesShort')}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label={t('common.staff')}>
                <select
                  className="select"
                  required
                  value={form.staff_id}
                  onChange={(event) => setForm({ ...form, staff_id: event.target.value })}
                >
                  <option value="">{t('bookingsPage.selectStaff')}</option>
                  {activeStaff.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.full_name}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label={t('bookingsPage.startTime')}>
                <input
                  className="input"
                  type="datetime-local"
                  required
                  value={form.start_time}
                  onChange={(event) => setForm({ ...form, start_time: event.target.value })}
                />
              </FormField>
              <FormField label={t('bookingsPage.note')}>
                <textarea
                  className="textarea"
                  value={form.note}
                  onChange={(event) => setForm({ ...form, note: event.target.value })}
                />
              </FormField>
              <button className="btn btn-primary w-full" disabled={submitting || activeServices.length === 0 || activeStaff.length === 0}>
                <Plus size={17} strokeWidth={1.8} />
                {submitting ? t('bookingsPage.creating') : t('bookingsPage.create')}
              </button>
            </form>
          </Panel>

          <Panel>
            <div className="mb-5 grid gap-3 lg:grid-cols-4">
              <input
                className="input"
                type="date"
                value={filters.date}
                onChange={(event) => setFilters({ ...filters, date: event.target.value })}
                aria-label={t('bookingsPage.filterDate')}
              />
              <select
                className="select"
                value={filters.status}
                onChange={(event) => setFilters({ ...filters, status: event.target.value })}
                aria-label={t('bookingsPage.filterStatus')}
              >
                <option value="">{t('bookingsPage.allStatuses')}</option>
                <option value="pending">{t('status.pending')}</option>
                <option value="confirmed">{t('status.confirmed')}</option>
                <option value="completed">{t('status.completed')}</option>
                <option value="cancelled">{t('status.cancelled')}</option>
                <option value="no_show">{t('status.no_show')}</option>
              </select>
              <select
                className="select"
                value={filters.staff_id}
                onChange={(event) => setFilters({ ...filters, staff_id: event.target.value })}
                aria-label={t('bookingsPage.filterStaff')}
              >
                <option value="">{t('bookingsPage.allStaff')}</option>
                {staff.map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.full_name}
                  </option>
                ))}
              </select>
              <select
                className="select"
                value={filters.service_id}
                onChange={(event) => setFilters({ ...filters, service_id: event.target.value })}
                aria-label={t('bookingsPage.filterService')}
              >
                <option value="">{t('bookingsPage.allServices')}</option>
                {services.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
              </select>
            </div>

            {loading ? (
              <div className="grid gap-3">
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
              </div>
            ) : bookings.length === 0 ? (
              <EmptyState title={t('bookingsPage.emptyTitle')} description={t('bookingsPage.emptyText')} />
            ) : (
              <div className="overflow-x-auto rounded-2xl ring-1 ring-qabul-ink/5">
                <table className="w-full min-w-[820px] border-collapse bg-white">
                  <thead className="bg-qabul-wash">
                    <tr>
                      <th className="table-th">{t('common.client')}</th>
                      <th className="table-th">{t('common.service')}</th>
                      <th className="table-th">{t('common.staff')}</th>
                      <th className="table-th">{t('common.time')}</th>
                      <th className="table-th">{t('common.status')}</th>
                      <th className="table-th text-right">{t('common.actions')}</th>
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
                        <td className="table-td">{booking.staff_name}</td>
                        <td className="table-td font-mono text-xs">{formatDateTime(booking.start_time)}</td>
                        <td className="table-td">
                          <Badge tone={statusTone[booking.status] || 'graphite'}>{t(`status.${booking.status}`)}</Badge>
                        </td>
                        <td className="table-td">
                          <div className="flex justify-end gap-2">
                            {booking.status === 'confirmed' || booking.status === 'pending' ? (
                              <>
                                <button
                                  className="btn btn-secondary size-9 p-0"
                                  onClick={() => changeStatus(booking.id, 'completed')}
                                  aria-label={t('bookingsPage.markCompleted')}
                                >
                                  <CheckCircle2 size={16} strokeWidth={1.8} />
                                </button>
                                <button
                                  className="btn btn-secondary size-9 p-0"
                                  onClick={() => cancelBooking(booking.id)}
                                  aria-label={t('bookingsPage.cancelBooking')}
                                >
                                  <Ban size={16} strokeWidth={1.8} />
                                </button>
                              </>
                            ) : (
                              <button
                                className="btn btn-secondary size-9 p-0"
                                onClick={() => changeStatus(booking.id, 'confirmed')}
                                aria-label={t('bookingsPage.restoreBooking')}
                              >
                                <RefreshCcw size={16} strokeWidth={1.8} />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>
        </div>
      )}
    </>
  )
}
