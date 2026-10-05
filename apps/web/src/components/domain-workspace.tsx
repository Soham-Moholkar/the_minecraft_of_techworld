import Link from "next/link";
import { ArrowRight, FileCode2, Layers3 } from "lucide-react";
import type { OperationalDomain } from "@/data/operations";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

export function DomainWorkspace({ domain }: { domain: OperationalDomain }) {
  return <div className="space-y-6">
    <section className="flex flex-col justify-between gap-4 border-b border-white/[.07] pb-6 md:flex-row md:items-end"><div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300"><Layers3 size={13}/>Source inventory</div><h1 className="mt-2 text-3xl font-semibold">{domain.title}</h1><p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-500">{domain.summary}</p></div><Badge tone="neutral">{domain.posture}</Badge></section>
    <p className="text-xs text-slate-500">Implementation inventory. Runtime availability and verification results are shown by the service diagnostics and test center.</p><div className="grid gap-4 lg:grid-cols-3">{domain.items.map((item) => <Card key={item.name} className="flex flex-col p-5"><div className="flex items-start justify-between gap-3"><div className="grid size-9 place-items-center rounded-lg bg-cyan-300/[.08] text-cyan-300"><FileCode2 size={16}/></div><Badge tone={item.status === "reference" ? "neutral" : "info"}>{item.status}</Badge></div><h2 className="mt-5 text-sm font-semibold">{item.name}</h2><p className="mt-1 text-[10px] leading-relaxed text-slate-500">{item.kind}</p><div className="mt-5 border-t border-white/[.07] pt-4"><div className="text-[9px] text-slate-600">Owner</div><div className="mt-1 text-[10px] text-slate-300">{item.owner}</div><div className="mt-3 text-[9px] text-slate-600">Evidence</div><div className="mt-1 break-all font-mono text-[9px] text-cyan-200">{item.evidence}</div></div></Card>)}</div>
    <Card className="flex flex-col items-start justify-between gap-4 p-5 sm:flex-row sm:items-center"><div><h2 className="text-sm font-semibold">Engineering progression</h2><p className="mt-1 text-[10px] text-slate-500">Inspect implemented levels, tests, source paths, and the next bounded increment.</p></div><Link href="/developer/technologies" className="flex items-center gap-1 text-xs font-semibold text-cyan-300">Open progression <ArrowRight size={13}/></Link></Card>
  </div>;
}
