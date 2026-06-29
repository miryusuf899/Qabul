import { useEffect, useState } from 'react'
import { Check, Pencil, Plus, Power } from 'lucide-react'

import { api, getErrorMessage } from '../api/client.js'
import { Badge } from '../components/ui/Badge.jsx'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { FormField } from '../components/ui/FormField.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'
import { useLanguage } from '../context/LanguageContext.jsx'
import { money } from '../utils/format.js'

const emptyForm = {
  name: '',
  description: '',
  price: '',
  duration_minutes: 30,
  is_active: true,
}

export function ServicesPage() {
  const { selectedBusinessId } = useBusiness()
  const { t } = useLanguage()
  const [services, setServices] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function loadServices() {
    if (!selectedBusinessId) return
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get(`/businesses/${selectedBusinessId}/services`)
      setServices(data)
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось загрузить услуги'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadServices()
  }, [selectedBusinessId])

  function startEdit(service) {
    setEditingId(service.id)
    setForm({
      name: service.name,
      description: service.description || '',
      price: String(service.price),
      duration_minutes: service.duration_minutes,
      is_active: service.is_active,
    })
  }

  function resetForm() {
    setEditingId(null)
    setForm(emptyForm)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!selectedBusinessId) return
    setSubmitting(true)
    setError('')
    const payload = {
      ...form,
      description: form.description || null,
      price: Number(form.price),
      duration_minutes: Number(form.duration_minutes),
    }
    try {
      if (editingId) {
        await api.put(`/services/${editingId}`, payload)
      } else {
        await api.post(`/businesses/${selectedBusinessId}/services`, payload)
      }
      resetForm()
      await loadServices()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось сохранить услугу'))
    } finally {
      setSubmitting(false)
    }
  }

  async function disableService(serviceId) {
    setError('')
    try {
      await api.delete(`/services/${serviceId}`)
      await loadServices()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось выключить услугу'))
    }
  }

  return (
    <>
      <PageHeader
        title={t('servicesPage.title')}
        description={t('servicesPage.description')}
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            {t('servicesPage.addAction')}
          </button>
        }
      />
      {!selectedBusinessId ? (
        <Panel>
          <EmptyState title={t('servicesPage.noBusinessTitle')} description={t('servicesPage.noBusinessText')} />
        </Panel>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[0.72fr_1.28fr]">
          <Panel>
            <h2 className="text-lg font-black tracking-[-0.035em]">
              {editingId ? t('servicesPage.editTitle') : t('servicesPage.addTitle')}
            </h2>
            <p className="mt-1 text-sm leading-6 text-qabul-muted">
              {t('servicesPage.formText')}
            </p>
            <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
              {error ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
              <FormField label={t('common.name')}>
                <input
                  className="input"
                  required
                  minLength={2}
                  value={form.name}
                  onChange={(event) => setForm({ ...form, name: event.target.value })}
                />
              </FormField>
              <FormField label={t('common.description')}>
                <textarea
                  className="textarea"
                  value={form.description}
                  onChange={(event) => setForm({ ...form, description: event.target.value })}
                />
              </FormField>
              <div className="grid gap-4 sm:grid-cols-2">
                <FormField label={t('common.price')}>
                  <input
                    className="input"
                    type="number"
                    min="0"
                    step="0.01"
                    required
                    value={form.price}
                    onChange={(event) => setForm({ ...form, price: event.target.value })}
                  />
                </FormField>
                <FormField label={t('servicesPage.duration')}>
                  <input
                    className="input"
                    type="number"
                    min="1"
                    required
                    value={form.duration_minutes}
                    onChange={(event) => setForm({ ...form, duration_minutes: event.target.value })}
                  />
                </FormField>
              </div>
              <label className="flex items-center justify-between rounded-2xl bg-qabul-wash px-4 py-3 text-sm font-semibold text-qabul-ink ring-1 ring-qabul-ink/5">
                {t('common.active')}
                <input
                  className="size-5 accent-qabul-leaf"
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(event) => setForm({ ...form, is_active: event.target.checked })}
                />
              </label>
              <div className="flex gap-2">
                <button className="btn btn-primary flex-1" disabled={submitting}>
                  <Check size={17} strokeWidth={1.8} />
                  {submitting ? t('common.saving') : t('common.save')}
                </button>
                {editingId ? (
                  <button type="button" className="btn btn-secondary" onClick={resetForm}>
                    {t('common.cancel')}
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
            ) : services.length === 0 ? (
              <EmptyState title={t('servicesPage.emptyTitle')} description={t('servicesPage.emptyText')} />
            ) : (
              <div className="overflow-hidden rounded-2xl ring-1 ring-qabul-ink/5">
                <table className="w-full border-collapse bg-white">
                  <thead className="bg-qabul-wash">
                    <tr>
                      <th className="table-th">{t('servicesPage.tableService')}</th>
                      <th className="table-th">{t('common.price')}</th>
                      <th className="table-th">{t('common.duration')}</th>
                      <th className="table-th">{t('common.status')}</th>
                      <th className="table-th text-right">{t('common.actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {services.map((service) => (
                      <tr key={service.id} className="transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-qabul-wash/70">
                        <td className="table-td">
                          <div className="font-semibold text-qabul-ink">{service.name}</div>
                          <div className="max-w-md truncate text-xs text-qabul-muted">
                            {service.description || t('common.noDescription')}
                          </div>
                        </td>
                        <td className="table-td font-mono text-xs">{money(service.price)}</td>
                        <td className="table-td font-mono text-xs">{service.duration_minutes} {t('common.minutesShort')}</td>
                        <td className="table-td">
                          <Badge tone={service.is_active ? 'green' : 'graphite'}>
                            {service.is_active ? t('common.active') : t('common.off')}
                          </Badge>
                        </td>
                        <td className="table-td">
                          <div className="flex justify-end gap-2">
                            <button className="btn btn-secondary size-9 p-0" onClick={() => startEdit(service)} aria-label={t('servicesPage.edit')}>
                              <Pencil size={16} strokeWidth={1.8} />
                            </button>
                            {service.is_active ? (
                              <button
                                className="btn btn-secondary size-9 p-0"
                                onClick={() => disableService(service.id)}
                                aria-label={t('servicesPage.disable')}
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
