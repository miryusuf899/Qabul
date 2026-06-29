import { Plus } from 'lucide-react'

import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'

export function StaffPage() {
  return (
    <>
      <PageHeader
        title="Staff"
        description="Assign services to each master and keep schedules clean."
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            Add staff
          </button>
        }
      />
      <Panel>
        <div className="skeleton h-80 w-full" />
      </Panel>
    </>
  )
}
