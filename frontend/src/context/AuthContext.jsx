import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api, getErrorMessage } from '../api/client.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [token, setToken] = useState(() => localStorage.getItem('qabul_token'))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(token))

  useEffect(() => {
    let cancelled = false
    async function loadUser() {
      if (!token) {
        setLoading(false)
        return
      }
      try {
        const { data } = await api.get('/auth/me')
        if (!cancelled) setUser(data)
      } catch {
        localStorage.removeItem('qabul_token')
        if (!cancelled) {
          setToken(null)
          setUser(null)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadUser()
    return () => {
      cancelled = true
    }
  }, [token])

  async function login(payload) {
    try {
      const { data } = await api.post('/auth/login', payload)
      localStorage.setItem('qabul_token', data.access_token)
      setToken(data.access_token)
      setUser(data.user)
      navigate('/', { replace: true })
      return { ok: true }
    } catch (error) {
      return { ok: false, error: getErrorMessage(error, 'Не удалось войти') }
    }
  }

  async function register(payload) {
    try {
      await api.post('/auth/register', payload)
      return await login({ email: payload.email, password: payload.password })
    } catch (error) {
      return { ok: false, error: getErrorMessage(error, 'Не удалось создать аккаунт') }
    }
  }

  function logout() {
    localStorage.removeItem('qabul_token')
    setToken(null)
    setUser(null)
    navigate('/login', { replace: true })
  }

  const value = useMemo(
    () => ({ token, user, loading, login, register, logout }),
    [token, user, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
