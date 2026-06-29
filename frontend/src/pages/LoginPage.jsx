import { useState } from 'react'
import { Link } from 'react-router-dom'

import { AuthFrame } from '../components/auth/AuthFrame.jsx'
import { FormField } from '../components/ui/FormField.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export function LoginPage() {
  const { login } = useAuth()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    const result = await login(form)
    if (!result.ok) setError(result.error)
    setSubmitting(false)
  }

  return (
    <AuthFrame
      title="Вход в dashboard"
      description="Управляйте записями, услугами и клиентами из одной панели."
    >
      <form className="grid gap-5" onSubmit={handleSubmit}>
        {error ? <div className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</div> : null}
        <FormField label="Email">
          <input
            className="input"
            type="email"
            required
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
          />
        </FormField>
        <FormField label="Password">
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
          {submitting ? 'Входим' : 'Войти'}
        </button>
        <p className="text-center text-sm text-qabul-muted">
          Нет аккаунта?{' '}
          <Link className="font-semibold text-qabul-leaf hover:text-qabul-leafDark" to="/register">
            Зарегистрироваться
          </Link>
        </p>
      </form>
    </AuthFrame>
  )
}
