import { Outlet } from 'react-router-dom'

import { Navbar } from './Navbar.jsx'
import { Sidebar } from './Sidebar.jsx'

export function AppShell() {
  return (
    <div className="min-h-[100dvh] text-qabul-ink">
      <Sidebar />
      <div className="min-h-[100dvh] lg:pl-[18rem]">
        <Navbar />
        <main id="main-content" className="mx-auto w-full max-w-[1480px] px-4 pb-10 pt-4 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
