import Link from "next/link";
import { ArrowRight, Layers3 } from "lucide-react";
import { operationalDomains } from "@/data/operations";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

export default function CatalogPage() {
  return <div className="space-y-6"><section><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300"><Layers3 size={13}/>Capability map</div><h1 className="mt-2 text-3xl font-semibold">Domain catalog</h1><p className="mt-2 max-w-3xl text-sm text-slate-500">Every visible domain resolves to owned capabilities and inspectable evidence—implemented, verified, or explicitly tracked.</p></section><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{Object.values(operationalDomains).map((domain) => <Link href={`/${domain.id}`} key={domain.id}><Card className="group h-full p-5 transition hover:-translate-y-0.5 hover:border-cyan-300/20"><div className="flex items-start justify-between"><div className="grid size-9 place-items-center rounded-lg bg-cyan-300/[.08] text-cyan-300"><Layers3 size={16}/></div><Badge>{domain.items.length} capabilities</Badge></div><h2 className="mt-5 text-base font-semibold">{domain.title}</h2><p className="mt-2 text-xs leading-relaxed text-slate-500">{domain.summary}</p><div className="mt-5 flex items-center gap-1 text-[10px] font-semibold text-cyan-300">Inspect evidence <ArrowRight size={12} className="transition group-hover:translate-x-0.5"/></div></Card></Link>)}</div></div>;
}
