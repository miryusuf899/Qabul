import { useState } from 'react'
import { Link } from 'react-router-dom'

import { AuthFrame } from '../components/auth/AuthFrame.jsx'
import { FormField } from '../components/ui/FormField.jsx'
import { useAuth } from '../context/AuthContext.jsx'
import { useLanguage } from '../context/LanguageContext.jsx'

export function RegisterPage() {
  const { register } = useAuth()
  const { t } = useLanguage()
  const [form, setForm] = useState({ full_name: '', email: '', phone: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    const result = await register(form)
    if (!result.ok) setError(result.error)
    setSubmitting(false)
  }

  return (
    <AuthFrame
      title={t('auth.registerTitle')}
      description={t('auth.registerDescription')}
    >
      <form className="grid gap-5" onSubmit={handleSubmit}>
        {error ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
        <FormField label={t('common.fullName')}>
          <input
            className="input"
            required
            minLength={2}
            value={form.full_name}
            onChange={(event) => setForm({ ...form, full_name: event.target.value })}
          />
        </FormField>
        <FormField label={t('common.email')}>
          <input
            className="input"
            type="email"
            required
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
          />
        </FormField>
        <FormField label={t('common.phone')}>
          <input
            className="input"
            value={form.phone}
            onChange={(event) => setForm({ ...form, phone: event.target.value })}
          />
        </FormField>
        <FormField label={t('common.password')}>
          <input
            className="input"
            type="password"
            required
            minLength={6}
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </FormField>
        <button className="btn btn-primary w-full" disabled={submitting}>
          {submitting ? t('auth.registering') : t('auth.registerButton')}
        </button>
        <p className="text-center text-sm text-qabul-muted">
          {t('auth.hasAccount')}{' '}
          <Link className="font-semibold text-qabul-leaf hover:text-qabul-leafDark" to="/login">
            {t('auth.loginLink')}
          </Link>
        </p>
      </form>
    </AuthFrame>
  )
}
