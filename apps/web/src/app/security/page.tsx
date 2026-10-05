import { LockKeyhole, ShieldCheck } from "lucide-react";
import { AuditLog } from "@/components/audit-log";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

export default function SecurityPage() {
  return <div className="space-y-6"><section className="flex flex-col justify-between gap-4 border-b border-white/[.07] pb-6 md:flex-row md:items-end"><div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300"><ShieldCheck size={13}/>Security operations</div><h1 className="mt-2 text-3xl font-semibold">Security posture</h1><p className="mt-2 text-sm text-slate-500">Tenant boundaries, authentication evidence, and remediation work.</p></div><Badge tone="success">Tenant boundary enforced</Badge></section><div className="grid gap-3 md:grid-cols-3">{[["Authentication","Local provider seam","OIDC next"],["Authorization","Organization scoped","5 regression tests"],["Audit integrity","Atomic transaction","Immutable events"]].map(([label,value,meta])=><Card key={label} className="p-4"><LockKeyhole size={16} className="text-cyan-300"/><div className="mt-4 text-[10px] text-slate-500">{label}</div><div className="mt-1 text-sm font-semibold">{value}</div><div className="mt-1 text-[9px] text-slate-600">{meta}</div></Card>)}</div><AuditLog/></div>;
}

