import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

import { api, getErrorMessage } from '../api/client.js'
import { useAuth } from './AuthContext.jsx'

const BusinessContext = createContext(null)

export function BusinessProvider({ children }) {
  const { token } = useAuth()
  const [businesses, setBusinesses] = useState([])
  const [selectedBusinessId, setSelectedBusinessIdState] = useState(() => {
    const value = localStorage.getItem('qabul_business_id')
    return value ? Number(value) : null
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const refreshBusinesses = useCallback(
    async (options = {}) => {
      if (!token) {
        setBusinesses([])
        setSelectedBusinessIdState(null)
        return []
      }
      setLoading(true)
      setError('')
      try {
        const { data } = await api.get('/businesses')
        setBusinesses(data)
        const preferredId = options.preferredId || selectedBusinessId
        const currentStillExists = data.some((business) => business.id === preferredId)
        if (!currentStillExists) {
          const nextId = data[0]?.id || null
          setSelectedBusinessIdState(nextId)
          if (nextId) localStorage.setItem('qabul_business_id', String(nextId))
        } else if (preferredId) {
          setSelectedBusinessIdState(preferredId)
          localStorage.setItem('qabul_business_id', String(preferredId))
        }
        return data
      } catch (requestError) {
        setError(getErrorMessage(requestError, 'Не удалось загрузить бизнесы'))
        return []
      } finally {
        setLoading(false)
      }
    },
    [token, selectedBusinessId],
  )

  useEffect(() => {
    let cancelled = false
    async function load() {
      if (!cancelled) await refreshBusinesses()
    }
    load()
    return () => {
      cancelled = true
    }
  }, [refreshBusinesses])

  function setSelectedBusinessId(id) {
    setSelectedBusinessIdState(id)
    if (id) {
      localStorage.setItem('qabul_business_id', String(id))
    }
  }

  async function createBusiness(payload) {
    try {
      const cleanPayload = Object.fromEntries(
        Object.entries(payload).map(([key, value]) => [key, value === '' ? null : value]),
      )
      const { data } = await api.post('/businesses', cleanPayload)
      await refreshBusinesses({ preferredId: data.id })
      return { ok: true, business: data }
    } catch (requestError) {
      return { ok: false, error: getErrorMessage(requestError, 'Не удалось создать бизнес') }
    }
  }

  const selectedBusiness = businesses.find((business) => business.id === selectedBusinessId) || null

  const value = useMemo(
    () => ({
      businesses,
      selectedBusiness,
      selectedBusinessId,
      setSelectedBusinessId,
      loading,
      error,
      refreshBusinesses,
      createBusiness,
    }),
    [businesses, selectedBusiness, selectedBusinessId, loading, error, refreshBusinesses],
  )

  return <BusinessContext.Provider value={value}>{children}</BusinessContext.Provider>
}

export function useBusiness() {
  const context = useContext(BusinessContext)
  if (!context) {
    throw new Error('useBusiness must be used inside BusinessProvider')
  }
  return context
}
