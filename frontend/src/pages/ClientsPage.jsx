import { PageHeader } from '../components/ui/PageHeader.jsx'
import { Panel } from '../components/ui/Panel.jsx'

export function ClientsPage() {
  return (
    <>
      <PageHeader title="Clients" description="View client history, Telegram profiles and contact details." />
      <Panel>
        <div className="skeleton h-80 w-full" />
      </Panel>
    </>
  )
}
