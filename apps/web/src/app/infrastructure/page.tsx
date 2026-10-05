import { DeploymentWorkspace } from "@/components/deployment-workspace";
import { InfrastructurePlanWorkspace } from "@/components/infrastructure-plan-workspace";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { operationalDomains } from "@/data/operations";
export default function InfrastructurePage() {
  return <div className="space-y-6"><header><p className="text-xs font-medium uppercase tracking-widest text-cyan-400">Platform operations · Phase 11</p><h1 className="mt-2 text-3xl font-semibold">Infrastructure</h1><p className="mt-2 max-w-3xl text-sm text-slate-500">Review the owned development deployment before bringing it to a cluster. Inspect resource budgets, isolation policy and the data that teardown retains.</p></header><InfrastructurePlanWorkspace/><DeploymentWorkspace/><Card className="p-5"><details><summary className="cursor-pointer font-semibold">Existing runtime source inventory</summary><p className="my-3 text-xs text-slate-500">Owned implementation locations; live availability is unverified.</p><ul className="space-y-3">{operationalDomains.infrastructure.items.map(item => <li key={item.name}><h2 className="text-sm font-medium">{item.name}</h2><p className="mt-1 text-xs text-slate-500">{item.kind}</p><p className="mt-1 break-all font-mono text-xs text-cyan-200">{item.evidence}</p></li>)}</ul><Link className="mt-4 inline-block text-xs text-cyan-300" href="/developer/technologies">Inspect engineering progression</Link></details></Card></div>;
}
