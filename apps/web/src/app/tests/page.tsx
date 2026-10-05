import { CheckCircle2, CircleX, Clock3, FlaskConical, TerminalSquare } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import snapshot from "@/data/quality-snapshot.json";

type QualityGate = {
  id: string;
  name: string;
  command: string;
  status: "passed" | "failed" | "not_run";
  duration_ms: number;
  executed_at?: string;
};
const gates = snapshot.gates as QualityGate[];

export default function TestCenterPage() {
  const notRun = gates.filter(gate => gate.status === "not_run").length;
  const duration = gates.reduce((total, gate) => total + gate.duration_ms, 0);
  return <div className="space-y-6"><section className="flex flex-col justify-between gap-4 border-b border-white/[.07] pb-6 md:flex-row md:items-end"><div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300"><FlaskConical size={13}/>Quality operations</div><h1 className="mt-2 text-3xl font-semibold">Test center</h1><p className="mt-2 text-sm text-slate-500">Recorded quality evidence. Unselected gates are not run; this snapshot does not certify running services.</p></div><Badge tone={snapshot.summary.failed > 0 ? "danger" : notRun > 0 ? "neutral" : "success"}>{snapshot.summary.passed}/{snapshot.summary.total} gates passed</Badge></section>
    <div className="grid gap-3 sm:grid-cols-4"><Card className="p-4"><div className="text-[10px] text-slate-500">Passing gates</div><div className="mt-2 text-2xl font-semibold text-emerald-300">{snapshot.summary.passed}</div></Card><Card className="p-4"><div className="text-[10px] text-slate-500">Failed gates</div><div className="mt-2 text-2xl font-semibold text-rose-300">{snapshot.summary.failed}</div></Card><Card className="p-4"><div className="text-[10px] text-slate-500">Not run</div><div className="mt-2 text-2xl font-semibold">{notRun}</div></Card><Card className="p-4"><div className="text-[10px] text-slate-500">Aggregate duration</div><div className="mt-2 text-2xl font-semibold">{(duration / 1000).toFixed(1)}s</div></Card></div>
    <Card className="overflow-hidden"><div className="grid grid-cols-[1fr_110px_110px] border-b border-white/[.07] bg-white/[.02] px-5 py-3 text-[9px] font-bold uppercase tracking-[.14em] text-slate-600"><span>Gate</span><span>Status</span><span>Duration</span></div>{gates.map((gate)=><div key={gate.id} className="grid grid-cols-[1fr_110px_110px] items-center border-b border-white/[.06] px-5 py-4 last:border-0"><div><div className="flex items-center gap-2 text-xs font-semibold"><TerminalSquare size={14} className="text-slate-500"/>{gate.name}</div><div className="mt-1 truncate font-mono text-[9px] text-slate-600">{gate.command}</div><p className="mt-1 break-all text-[9px] text-slate-500">{gate.executed_at ? <>Checked <time dateTime={gate.executed_at}>{gate.executed_at}</time></> : "No recorded check"}</p></div><div className={`flex items-center gap-1 text-[10px] font-semibold ${gate.status === "passed" ? "text-emerald-300" : gate.status === "not_run" ? "text-slate-500" : "text-rose-300"}`}>{gate.status === "passed" ? <CheckCircle2 size={13}/> : gate.status === "not_run" ? <Clock3 size={13}/> : <CircleX size={13}/>} {gate.status}</div><div className="flex items-center gap-1 text-[10px] text-slate-500"><Clock3 size={12}/>{(gate.duration_ms/1000).toFixed(2)}s</div></div>)}</Card>
    <p className="text-[9px] text-slate-600">Generated {snapshot.generated_at} · run <code>node scripts/quality-snapshot.mjs {snapshot.profile}</code> to refresh.</p>
  </div>;
}
