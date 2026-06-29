import { useEffect, useMemo, useState } from 'react'
import { Check, Pencil } from 'lucide-react'

import { api, getErrorMessage } from '../api/client.js'
import { EmptyState } from '../components/ui/EmptyState.jsx'
import { FormField } from '../components/ui/FormField.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'
import { useLanguage } from '../context/LanguageContext.jsx'
import { formatDateTime } from '../utils/format.js'

export function ClientsPage() {
  const { selectedBusinessId } = useBusiness()
  const { t } = useLanguage()
  const [clients, setClients] = useState([])
  const [selectedClient, setSelectedClient] = useState(null)
  const [form, setForm] = useState({ full_name: '', phone: '', telegram_username: '' })
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const filteredClients = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    if (!normalized) return clients
    return clients.filter((client) =>
      [client.full_name, client.phone, client.telegram_username]
        .filter(Boolean)
        .some((value) => value.toLowerCase().includes(normalized)),
    )
  }, [clients, query])

  async function loadClients() {
    if (!selectedBusinessId) return
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get(`/businesses/${selectedBusinessId}/clients`)
      setClients(data)
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось загрузить клиентов'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadClients()
  }, [selectedBusinessId])

  function startEdit(client) {
    setSelectedClient(client)
    setForm({
      full_name: client.full_name || '',
      phone: client.phone || '',
      telegram_username: client.telegram_username || '',
    })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!selectedClient) return
    setSubmitting(true)
    setError('')
    try {
      await api.put(`/clients/${selectedClient.id}`, {
        full_name: form.full_name || null,
        phone: form.phone || null,
        telegram_username: form.telegram_username || null,
      })
      setSelectedClient(null)
      setForm({ full_name: '', phone: '', telegram_username: '' })
      await loadClients()
    } catch (requestError) {
      setError(getErrorMessage(requestError, 'Не удалось сохранить клиента'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <PageHeader title={t('clientsPage.title')} description={t('clientsPage.description')} />
      {!selectedBusinessId ? (
        <Panel>
          <EmptyState title={t('clientsPage.noBusinessTitle')} description={t('clientsPage.noBusinessText')} />
        </Panel>
      ) : (
        <div className="grid gap-5 xl:grid-cols-[1.28fr_0.72fr]">
          <Panel>
            <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-lg font-black tracking-[-0.035em]">{t('clientsPage.baseTitle')}</h2>
                <p className="text-sm text-qabul-muted">{t('clientsPage.baseText')}</p>
              </div>
              <input
                className="input max-w-sm"
                type="search"
                placeholder={t('clientsPage.search')}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </div>
            {error ? <div className="mb-4 rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
            {loading ? (
              <div className="grid gap-3">
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
                <div className="skeleton h-16" />
              </div>
            ) : filteredClients.length === 0 ? (
              <EmptyState title={t('clientsPage.emptyTitle')} description={t('clientsPage.emptyText')} />
            ) : (
              <div className="overflow-x-auto rounded-2xl ring-1 ring-qabul-ink/5">
                <table className="w-full min-w-[720px] border-collapse bg-white">
                  <thead className="bg-qabul-wash">
                    <tr>
                      <th className="table-th">{t('common.client')}</th>
                      <th className="table-th">{t('clientsPage.telegram')}</th>
                      <th className="table-th">{t('clientsPage.visits')}</th>
                      <th className="table-th">{t('clientsPage.lastVisit')}</th>
                      <th className="table-th text-right">{t('common.actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredClients.map((client) => (
                      <tr key={client.id} className="transition duration-300 ease-[cubic-bezier(0.32,0.72,0,1)] hover:bg-qabul-wash/70">
                        <td className="table-td">
                          <div className="font-semibold text-qabul-ink">{client.full_name || t('common.client')}</div>
                          <div className="text-xs text-qabul-muted">{client.phone || t('common.noPhone')}</div>
                        </td>
                        <td className="table-td">{client.telegram_username ? `@${client.telegram_username}` : t('common.noTelegram')}</td>
                        <td className="table-td font-mono text-xs">{client.total_visits}</td>
                        <td className="table-td font-mono text-xs">{client.last_visit_at ? formatDateTime(client.last_visit_at) : t('common.noVisits')}</td>
                        <td className="table-td">
                          <div className="flex justify-end">
                            <button className="btn btn-secondary size-9 p-0" onClick={() => startEdit(client)} aria-label={t('clientsPage.editClient')}>
                              <Pencil size={16} strokeWidth={1.8} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Panel>

          <Panel>
            <h2 className="text-lg font-black tracking-[-0.035em]">
              {selectedClient ? t('clientsPage.editClient') : t('clientsPage.details')}
            </h2>
            {selectedClient ? (
              <form className="mt-5 grid gap-4" onSubmit={handleSubmit}>
                <FormField label={t('common.fullName')}>
                  <input
                    className="input"
                    value={form.full_name}
                    onChange={(event) => setForm({ ...form, full_name: event.target.value })}
                  />
                </FormField>
                <FormField label={t('common.phone')}>
                  <input
                    className="input"
                    value={form.phone}
                    onChange={(event) => setForm({ ...form, phone: event.target.value })}
                  />
                </FormField>
                <FormField label={t('clientsPage.telegramUsername')}>
                  <input
                    className="input"
                    value={form.telegram_username}
                    onChange={(event) => setForm({ ...form, telegram_username: event.target.value })}
                  />
                </FormField>
                <div className="flex gap-2">
                  <button className="btn btn-primary flex-1" disabled={submitting}>
                    <Check size={17} strokeWidth={1.8} />
                    {submitting ? t('common.saving') : t('common.save')}
                  </button>
                  <button type="button" className="btn btn-secondary" onClick={() => setSelectedClient(null)}>
                    {t('common.cancel')}
                  </button>
                </div>
              </form>
            ) : (
              <EmptyState title={t('clientsPage.selectTitle')} description={t('clientsPage.selectText')} />
            )}
          </Panel>
        </div>
      )}
    </>
  )
}
