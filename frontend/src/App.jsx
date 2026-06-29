import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from './components/auth/ProtectedRoute.jsx'
import { AppShell } from './components/layout/AppShell.jsx'
import { PageLoader } from './components/ui/PageLoader.jsx'
import { LoginPage } from './pages/LoginPage.jsx'
import { NotFoundPage } from './pages/NotFoundPage.jsx'
import { RegisterPage } from './pages/RegisterPage.jsx'

const DashboardPage = lazy(() =>
  import('./pages/DashboardPage.jsx').then((module) => ({ default: module.DashboardPage })),
)
const ServicesPage = lazy(() =>
  import('./pages/ServicesPage.jsx').then((module) => ({ default: module.ServicesPage })),
)
const StaffPage = lazy(() =>
  import('./pages/StaffPage.jsx').then((module) => ({ default: module.StaffPage })),
)
const BookingsPage = lazy(() =>
  import('./pages/BookingsPage.jsx').then((module) => ({ default: module.BookingsPage })),
)
const ClientsPage = lazy(() =>
  import('./pages/ClientsPage.jsx').then((module) => ({ default: module.ClientsPage })),
)
const AnalyticsPage = lazy(() =>
  import('./pages/AnalyticsPage.jsx').then((module) => ({ default: module.AnalyticsPage })),
)

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="services" element={<ServicesPage />} />
          <Route path="staff" element={<StaffPage />} />
          <Route path="bookings" element={<BookingsPage />} />
          <Route path="clients" element={<ClientsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
        </Route>
        <Route path="/404" element={<NotFoundPage />} />
        <Route path="*" element={<Navigate to="/404" replace />} />
      </Routes>
    </Suspense>
  )
}
