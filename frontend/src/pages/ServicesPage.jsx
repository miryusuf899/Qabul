import { Plus } from 'lucide-react'

import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'

export function ServicesPage() {
  return (
    <>
      <PageHeader
        title="Services"
        description="Manage active services, prices and appointment duration."
        action={
          <button className="btn btn-primary">
            <Plus size={17} strokeWidth={1.8} />
            Add service
          </button>
        }
      />
      <Panel>
        <div className="skeleton h-80 w-full" />
      </Panel>
    </>
  )
}
