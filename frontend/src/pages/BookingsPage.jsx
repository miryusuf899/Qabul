import { useEffect, useMemo, useState } from 'react'
import { Ban, CheckCircle2, Plus, RefreshCcw } from 'lucide-react'

import { api, getErrorMessage } from '../api/client.js'
import { Badge } from '../components/ui/Badge.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { FormField } from '../components/ui/FormField.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'
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
      await api.delete(`/bookings/${bookingId}`, { params: { reason: 'Cancelled from dashboard' } })
      await loadBookings()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось отменить запись'))
    }
  }

  return (
    <>
      <PageHeader
        title="Bookings"
        description="Create, cancel and track appointments without losing context."
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            New booking
          </button>
        }
      />
      {!selectedBusinessId ? (
        <Panel>
          <EmptyState title="No business selected" description="Select a business before managing bookings." />
        </Panel>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
          <Panel>
            <h2 className="text-lg font-black tracking-[-0.035em]">Create booking</h2>
            <p className="mt-1 text-sm leading-6 text-qabul-muted">
              Backend checks service, staff, working hours and conflicts.
            </p>
            <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
              {error ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
              <FormField label="Client name">
                <input
                  className="input"
                  value={form.client_name}
                  onChange={(event) => setForm({ ...form, client_name: event.target.value })}
                />
              </FormField>
              <FormField label="Client phone">
                <input
                  className="input"
                  value={form.client_phone}
                  onChange={(event) => setForm({ ...form, client_phone: event.target.value })}
                />
              </FormField>
              <FormField label="Service">
                <select
                  className="select"
                  required
                  value={form.service_id}
                  onChange={(event) => setForm({ ...form, service_id: event.target.value })}
                >
                  <option value="">Select service</option>
                  {activeServices.map((service) => (
                    <option key={service.id} value={service.id}>
                      {service.name} - {service.duration_minutes} min
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label="Staff">
                <select
                  className="select"
                  required
                  value={form.staff_id}
                  onChange={(event) => setForm({ ...form, staff_id: event.target.value })}
                >
                  <option value="">Select staff</option>
                  {activeStaff.map((member) => (
                    <option key={member.id} value={member.id}>
                      {member.full_name}
                    </option>
                  ))}
                </select>
              </FormField>
              <FormField label="Start time">
                <input
                  className="input"
                  type="datetime-local"
                  required
                  value={form.start_time}
                  onChange={(event) => setForm({ ...form, start_time: event.target.value })}
                />
              </FormField>
              <FormField label="Note">
                <textarea
                  className="textarea"
                  value={form.note}
                  onChange={(event) => setForm({ ...form, note: event.target.value })}
                />
              </FormField>
              <button className="btn btn-primary w-full" disabled={submitting || activeServices.length === 0 || activeStaff.length === 0}>
                <Plus size={17} strokeWidth={1.8} />
                {submitting ? 'Creating' : 'Create booking'}
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
                aria-label="Filter by date"
              />
              <select
                className="select"
                value={filters.status}
                onChange={(event) => setFilters({ ...filters, status: event.target.value })}
                aria-label="Filter by status"
              >
                <option value="">All statuses</option>
                <option value="pending">pending</option>
                <option value="confirmed">confirmed</option>
                <option value="completed">completed</option>
                <option value="cancelled">cancelled</option>
                <option value="no_show">no_show</option>
              </select>
              <select
                className="select"
                value={filters.staff_id}
                onChange={(event) => setFilters({ ...filters, staff_id: event.target.value })}
                aria-label="Filter by staff"
              >
                <option value="">All staff</option>
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
                aria-label="Filter by service"
              >
                <option value="">All services</option>
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
              <EmptyState title="No bookings found" description="Create a booking or change filters to see appointments." />
            ) : (
              <div className="overflow-x-auto rounded-2xl ring-1 ring-qabul-ink/5">
                <table className="w-full min-w-[820px] border-collapse bg-white">
                  <thead className="bg-qabul-wash">
                    <tr>
                      <th className="table-th">Client</th>
                      <th className="table-th">Service</th>
                      <th className="table-th">Staff</th>
                      <th className="table-th">Time</th>
                      <th className="table-th">Status</th>
                      <th className="table-th text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bookings.map((booking) => (
                      <tr key={booking.id} className="transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-qabul-wash/70">
                        <td className="table-td">
                          <div className="font-semibold text-qabul-ink">{booking.client_name || 'Client'}</div>
                          <div className="text-xs text-qabul-muted">{booking.client_phone || 'No phone'}</div>
                        </td>
                        <td className="table-td">
                          <div className="font-semibold text-qabul-ink">{booking.service_name}</div>
                          <div className="text-xs text-qabul-muted">{money(booking.service_price)}</div>
                        </td>
                        <td className="table-td">{booking.staff_name}</td>
                        <td className="table-td font-mono text-xs">{formatDateTime(booking.start_time)}</td>
                        <td className="table-td">
                          <Badge tone={statusTone[booking.status] || 'graphite'}>{booking.status}</Badge>
                        </td>
                        <td className="table-td">
                          <div className="flex justify-end gap-2">
                            {booking.status === 'confirmed' || booking.status === 'pending' ? (
                              <>
                                <button
                                  className="btn btn-secondary size-9 p-0"
                                  onClick={() => changeStatus(booking.id, 'completed')}
                                  aria-label="Mark completed"
                                >
                                  <CheckCircle2 size={16} strokeWidth={1.8} />
                                </button>
                                <button
                                  className="btn btn-secondary size-9 p-0"
                                  onClick={() => cancelBooking(booking.id)}
                                  aria-label="Cancel booking"
                                >
                                  <Ban size={16} strokeWidth={1.8} />
                                </button>
                              </>
                            ) : (
                              <button
                                className="btn btn-secondary size-9 p-0"
                                onClick={() => changeStatus(booking.id, 'confirmed')}
                                aria-label="Restore booking"
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
