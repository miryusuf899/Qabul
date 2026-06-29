import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'

export function AnalyticsPage() {
  return (
    <>
      <PageHeader title="Analytics" description="Revenue, bookings and service performance in one place." />
      <Panel>
        <div className="skeleton h-80 w-full" />
      </Panel>
    </>
  )
}
