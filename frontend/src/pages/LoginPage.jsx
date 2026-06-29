import { useState } from 'react'
import { Link } from 'react-router-dom'

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
    <main className="grid min-h-[100dvh] place-items-center px-4 py-10">
      <div className="surface-shell w-full max-w-md">
        <form className="surface-core grid gap-5 p-6" onSubmit={handleSubmit}>
          <div>
            <p className="text-sm font-semibold text-qabul-leaf">Qabul</p>
            <h1 className="mt-2 text-3xl font-black tracking-[-0.055em]">Вход в dashboard</h1>
            <p className="mt-2 text-sm leading-6 text-qabul-muted">
              Управляйте записями, услугами и клиентами из одной панели.
            </p>
          </div>
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
      </div>
    </main>
  )
}
