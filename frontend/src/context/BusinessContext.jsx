import { createContext, useContext, useEffect, useMemo, useState } from 'react'

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

  useEffect(() => {
    let cancelled = false
    async function loadBusinesses() {
      if (!token) {
        setBusinesses([])
        setSelectedBusinessIdState(null)
        return
      }
      setLoading(true)
      setError('')
      try {
        const { data } = await api.get('/businesses')
        if (cancelled) return
        setBusinesses(data)
        const currentStillExists = data.some((business) => business.id === selectedBusinessId)
        if (!currentStillExists) {
          const nextId = data[0]?.id || null
          setSelectedBusinessIdState(nextId)
          if (nextId) localStorage.setItem('qabul_business_id', String(nextId))
        }
      } catch (requestError) {
        if (!cancelled) setError(getErrorMessage(requestError, 'Не удалось загрузить бизнесы'))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadBusinesses()
    return () => {
      cancelled = true
    }
  }, [token, selectedBusinessId])

  function setSelectedBusinessId(id) {
    setSelectedBusinessIdState(id)
    if (id) {
      localStorage.setItem('qabul_business_id', String(id))
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
    }),
    [businesses, selectedBusiness, selectedBusinessId, loading, error],
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
