import { DomainWorkspace } from "@/components/domain-workspace";
import { LiveEvents } from "@/components/live-events";
import { RealtimeConsole } from "@/components/realtime-console";
import { operationalDomains } from "@/data/operations";

export default function ObservabilityPage() {
  return <div className="space-y-6"><DomainWorkspace domain={operationalDomains.observability}/><div className="grid gap-6 xl:grid-cols-2"><LiveEvents/><RealtimeConsole/></div></div>;
}
