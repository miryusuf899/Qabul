import { CalendarClock, Plus } from 'lucide-react'

import { EmptyState } from '../components/ui/EmptyState.jsx'
import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'
import { useBusiness } from '../context/BusinessContext.jsx'

export function DashboardPage() {
  const { selectedBusiness } = useBusiness()

  return (
    <>
      <PageHeader
        title={selectedBusiness ? `${selectedBusiness.name} dashboard` : 'Dashboard'}
        description="Bookings, revenue, clients and upcoming work for the selected business."
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            New booking
          </button>
        }
      />
      <div className="grid gap-5 xl:grid-cols-[1.35fr_0.65fr]">
        <Panel>
          <EmptyState
            title="Dashboard data will appear here"
            description="Select a business or create demo data to see bookings, revenue and client activity."
            action={
              <button className="btn btn-secondary">
                <CalendarClock size={17} strokeWidth={1.8} />
                Review bookings
              </button>
            }
          />
        </Panel>
        <Panel>
          <div className="grid gap-3">
            <div className="skeleton h-24" />
            <div className="skeleton h-24" />
            <div className="skeleton h-24" />
          </div>
        </Panel>
      </div>
    </>
  )
}
