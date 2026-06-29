import { useState } from 'react'

import { FormField } from '../ui/FormField.jsx'
import { useBusiness } from '../../context/BusinessContext.jsx'
import { useLanguage } from '../../context/LanguageContext.jsx'

const initialForm = {
  name: '',
  description: '',
  business_type: 'barbershop',
  phone: '',
  address: '',
  timezone: 'Asia/Dushanbe',
  ai_enabled: true,
}

export function BusinessCreateForm({ onCreated }) {
  const { createBusiness } = useBusiness()
  const { t } = useLanguage()
  const [form, setForm] = useState(initialForm)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    const result = await createBusiness(form)
    if (result.ok) {
      setForm(initialForm)
      onCreated?.(result.business)
    } else {
      setError(result.error)
    }
    setSubmitting(false)
  }

  return (
    <form className="grid gap-4" onSubmit={handleSubmit}>
      {error ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
      <div className="grid gap-4 md:grid-cols-2">
        <FormField label={t('business.name')}>
          <input
            className="input"
            required
            minLength={2}
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
          />
        </FormField>
        <FormField label={t('business.type')}>
          <select
            className="select"
            value={form.business_type}
            onChange={(event) => setForm({ ...form, business_type: event.target.value })}
          >
            <option value="barbershop">{t('business.types.barbershop')}</option>
            <option value="salon">{t('business.types.salon')}</option>
            <option value="clinic">{t('business.types.clinic')}</option>
            <option value="education">{t('business.types.education')}</option>
            <option value="fitness">{t('business.types.fitness')}</option>
            <option value="auto">{t('business.types.auto')}</option>
          </select>
        </FormField>
      </div>
      <FormField label={t('business.description')}>
        <textarea
          className="textarea"
          value={form.description}
          onChange={(event) => setForm({ ...form, description: event.target.value })}
        />
      </FormField>
      <div className="grid gap-4 md:grid-cols-2">
        <FormField label={t('business.phone')}>
          <input
            className="input"
            value={form.phone}
            onChange={(event) => setForm({ ...form, phone: event.target.value })}
          />
        </FormField>
        <FormField label={t('business.address')}>
          <input
            className="input"
            value={form.address}
            onChange={(event) => setForm({ ...form, address: event.target.value })}
          />
        </FormField>
      </div>
      <label className="flex items-center justify-between rounded-2xl bg-qabul-wash px-4 py-3 text-sm font-semibold text-qabul-ink ring-1 ring-qabul-ink/5">
        {t('business.ai')}
        <input
          type="checkbox"
          checked={form.ai_enabled}
          onChange={(event) => setForm({ ...form, ai_enabled: event.target.checked })}
          className="size-5 accent-qabul-leaf"
        />
      </label>
      <button className="btn btn-primary w-full" disabled={submitting}>
        {submitting ? t('business.creating') : t('business.create')}
      </button>
    </form>
  )
}
