import { Plus } from 'lucide-react'

import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'

export function BookingsPage() {
  return (
    <>
      <PageHeader
        title="Bookings"
        description="Create, cancel and track appointments without losing context."
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            New booking
          </button>
        }
      />
      <Panel>
        <div className="skeleton h-80 w-full" />
      </Panel>
    </>
  )
}
