import { useEffect, useState } from 'react'
import { Check, Pencil, Plus, Power } from 'lucide-react'

import { api, getErrorMessage } from '../api/client.js'
import { Badge } from '../components/ui/Badge.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { FormField } from '../components/ui/FormField.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'

const emptyForm = {
  full_name: '',
  phone: '',
  specialization: '',
  is_active: true,
  service_ids: [],
}

export function StaffPage() {
  const { selectedBusinessId } = useBusiness()
  const [staff, setStaff] = useState([])
  const [services, setServices] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function loadData() {
    if (!selectedBusinessId) return
    setLoading(true)
    setError('')
    try {
      const [staffResponse, servicesResponse] = await Promise.all([
        api.get(`/businesses/${selectedBusinessId}/staff`),
        api.get(`/businesses/${selectedBusinessId}/services`),
      ])
      setStaff(staffResponse.data)
      setServices(servicesResponse.data.filter((service) => service.is_active))
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось загрузить мастеров'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [selectedBusinessId])

  function resetForm() {
    setEditingId(null)
    setForm(emptyForm)
  }

  function startEdit(member) {
    setEditingId(member.id)
    setForm({
      full_name: member.full_name,
      phone: member.phone || '',
      specialization: member.specialization || '',
      is_active: member.is_active,
      service_ids: member.service_ids || [],
    })
  }

  function toggleService(serviceId) {
    const exists = form.service_ids.includes(serviceId)
    setForm({
      ...form,
      service_ids: exists
        ? form.service_ids.filter((id) => id !== serviceId)
        : [...form.service_ids, serviceId],
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!selectedBusinessId) return
    setSubmitting(true)
    setError('')
    const payload = {
      full_name: form.full_name,
      phone: form.phone || null,
      specialization: form.specialization || null,
      is_active: form.is_active,
    }
    try {
      if (editingId) {
        await api.put(`/staff/${editingId}`, payload)
        await api.post(`/staff/${editingId}/services`, { service_ids: form.service_ids })
      } else {
        await api.post(`/businesses/${selectedBusinessId}/staff`, {
          ...payload,
          service_ids: form.service_ids,
        })
      }
      resetForm()
      await loadData()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось сохранить мастера'))
    } finally {
      setSubmitting(false)
    }
  }

  async function disableStaff(staffId) {
    setError('')
    try {
      await api.delete(`/staff/${staffId}`)
      await loadData()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось выключить мастера'))
    }
  }

  function serviceNames(member) {
    const names = services
      .filter((service) => member.service_ids?.includes(service.id))
      .map((service) => service.name)
    return names.length ? names.join(', ') : 'No services'
  }

  return (
    <>
      <PageHeader
        title="Staff"
        description="Assign services to each master and keep schedules clean."
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            Add staff
          </button>
        }
      />
      {!selectedBusinessId ? (
        <Panel>
          <EmptyState title="No business selected" description="Select a business before adding staff." />
        </Panel>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
          <Panel>
            <h2 className="text-lg font-black tracking-[-0.035em]">
              {editingId ? 'Edit staff member' : 'Add staff member'}
            </h2>
            <p className="mt-1 text-sm leading-6 text-qabul-muted">
              Staff can only receive bookings for assigned services.
            </p>
            <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
              {error ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
              <FormField label="Full name">
                <input
                  className="input"
                  required
                  minLength={2}
                  value={form.full_name}
                  onChange={(event) => setForm({ ...form, full_name: event.target.value })}
                />
              </FormField>
              <FormField label="Phone">
                <input
                  className="input"
                  value={form.phone}
                  onChange={(event) => setForm({ ...form, phone: event.target.value })}
                />
              </FormField>
              <FormField label="Specialization">
                <input
                  className="input"
                  value={form.specialization}
                  onChange={(event) => setForm({ ...form, specialization: event.target.value })}
                />
              </FormField>
              <div>
                <p className="field-label mb-2">Services</p>
                <div className="grid gap-2">
                  {services.length === 0 ? (
                    <p className="rounded-xl bg-qabul-wash px-4 py-3 text-sm text-qabul-muted">
                      Add services first.
                    </p>
                  ) : (
                    services.map((service) => (
                      <label
                        key={service.id}
                        className="flex items-center justify-between rounded-2xl bg-qabul-wash px-4 py-3 text-sm font-semibold text-qabul-ink ring-1 ring-qabul-ink/5"
                      >
                        {service.name}
                        <input
                          className="size-5 accent-qabul-leaf"
                          type="checkbox"
                          checked={form.service_ids.includes(service.id)}
                          onChange={() => toggleService(service.id)}
                        />
                      </label>
                    ))
                  )}
                </div>
              </div>
              <label className="flex items-center justify-between rounded-2xl bg-qabul-wash px-4 py-3 text-sm font-semibold text-qabul-ink ring-1 ring-qabul-ink/5">
                Active
                <input
                  className="size-5 accent-qabul-leaf"
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(event) => setForm({ ...form, is_active: event.target.checked })}
                />
              </label>
              <div className="flex gap-2">
                <button className="btn btn-primary flex-1" disabled={submitting || services.length === 0}>
                  <Check size={17} strokeWidth={1.8} />
                  {submitting ? 'Saving' : 'Save'}
                </button>
                {editingId ? (
                  <button type="button" className="btn btn-secondary" onClick={resetForm}>
                    Cancel
                  </button>
                ) : null}
              </div>
            </form>
          </Panel>
          <Panel>
            {loading ? (
              <div className="grid gap-3">
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
              </div>
            ) : staff.length === 0 ? (
              <EmptyState title="No staff yet" description="Add masters and assign the services they can perform." />
            ) : (
              <div className="overflow-hidden rounded-2xl ring-1 ring-qabul-ink/5">
                <table className="w-full border-collapse bg-white">
                  <thead className="bg-qabul-wash">
                    <tr>
                      <th className="table-th">Name</th>
                      <th className="table-th">Services</th>
                      <th className="table-th">Status</th>
                      <th className="table-th text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {staff.map((member) => (
                      <tr key={member.id} className="transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-qabul-wash/70">
                        <td className="table-td">
                          <div className="font-semibold text-qabul-ink">{member.full_name}</div>
                          <div className="text-xs text-qabul-muted">{member.phone || member.specialization || 'No contact'}</div>
                        </td>
                        <td className="table-td max-w-md truncate">{serviceNames(member)}</td>
                        <td className="table-td">
                          <Badge tone={member.is_active ? 'green' : 'graphite'}>
                            {member.is_active ? 'active' : 'off'}
                          </Badge>
                        </td>
                        <td className="table-td">
                          <div className="flex justify-end gap-2">
                            <button className="btn btn-secondary size-9 p-0" onClick={() => startEdit(member)} aria-label="Edit staff">
                              <Pencil size={16} strokeWidth={1.8} />
                            </button>
                            {member.is_active ? (
                              <button
                                className="btn btn-secondary size-9 p-0"
                                onClick={() => disableStaff(member.id)}
                                aria-label="Disable staff"
                              >
                                <Power size={16} strokeWidth={1.8} />
                              </button>
                            ) : null}
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
