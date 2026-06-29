import { useState } from 'react'
import { Link } from 'react-router-dom'

import { FormField } from '../components/ui/FormField.jsx'
import { useAuth } from '../context/AuthContext.jsx'

export function RegisterPage() {
  const { register } = useAuth()
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
    <main className="grid min-h-[100dvh] place-items-center px-4 py-10">
      <div className="surface-shell w-full max-w-md">
        <form className="surface-core grid gap-5 p-6" onSubmit={handleSubmit}>
          <div>
            <p className="text-sm font-semibold text-qabul-leaf">Qabul</p>
            <h1 className="mt-2 text-3xl font-black tracking-[-0.055em]">Создать аккаунт</h1>
            <p className="mt-2 text-sm leading-6 text-qabul-muted">
              Подключите бизнес и начните принимать записи.
            </p>
          </div>
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
          <FormField label="Email">
            <input
              className="input"
              type="email"
              required
              value={form.email}
              onChange={(event) => setForm({ ...form, email: event.target.value })}
            />
          </FormField>
          <FormField label="Phone">
            <input
              className="input"
              value={form.phone}
              onChange={(event) => setForm({ ...form, phone: event.target.value })}
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
            {submitting ? 'Создаём' : 'Создать аккаунт'}
          </button>
          <p className="text-center text-sm text-qabul-muted">
            Уже есть аккаунт?{' '}
            <Link className="font-semibold text-qabul-leaf hover:text-qabul-leafDark" to="/login">
              Войти
            </Link>
          </p>
        </form>
      </div>
    </main>
  )
}
