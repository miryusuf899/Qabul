import { Navigate, useLocation } from 'react-router-dom'

import { PageLoader } from '../ui/PageLoader.jsx'
import { useAuth } from '../../context/AuthContext.jsx'

export function ProtectedRoute({ children }) {
  const location = useLocation()
  const { token, loading } = useAuth()

  if (loading) {
    return <PageLoader label="Проверяем доступ" />
  }

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  return children
}
