"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, CircleStop, FlaskConical, Play, RotateCcw, TerminalSquare } from "lucide-react";
import { nextLabStatus } from "@/lib/learning";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CodeBlock } from "@/components/code-block";

type Lab = {
  id: string;
  title: string;
  domain: string;
  difficulty: string;
  runtime: string;
  path: string;
  objective: string;
  commands: { start: string; test: string; reset: string };
};
type Status = "idle" | "ready" | "passed";

export function LabWorkspace({ lab }: { lab: Lab }) {
  const [status, setStatus] = useState<Status>("idle");
  const storageKey = `atlas-lab:${lab.id}`;

  useEffect(() => {
    queueMicrotask(() => {
      const saved = localStorage.getItem(storageKey);
      if (saved === "ready" || saved === "passed") setStatus(saved);
    });
  }, [storageKey]);

  function transition(action: "start" | "test" | "reset") {
    // This records evidence only; executable commands stay explicit in the IDE terminal.
    const next = nextLabStatus(status, action);
    setStatus(next);
    localStorage.setItem(storageKey, next);
  }

  return <div className="space-y-5">
    <section className="flex flex-col justify-between gap-4 border-b border-white/[.07] pb-6 md:flex-row md:items-end"><div><div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300"><FlaskConical size={14}/>Controlled workspace</div><h1 className="mt-2 text-3xl font-semibold">{lab.title}</h1><p className="mt-2 max-w-3xl text-sm text-slate-500">{lab.objective}</p></div><div className="flex gap-2"><Badge>{lab.difficulty}</Badge><Badge tone={status === "passed" ? "success" : status === "ready" ? "info" : "neutral"}>{status}</Badge></div></section>
    <div className="grid gap-5 lg:grid-cols-[1fr_340px]">
      <Card className="overflow-hidden"><div className="border-b border-white/[.07] p-5"><h2 className="text-sm font-semibold">Lifecycle commands</h2><p className="mt-1 text-[10px] text-slate-500">Run these from the repository root. The UI records your local lifecycle state; execution remains explicit and inspectable in the IDE terminal.</p></div><div className="space-y-4 p-5">{Object.entries(lab.commands).map(([action, command]) => <div key={action}><div className="mb-2 text-[9px] font-bold uppercase tracking-[.15em] text-slate-600">{action}</div><CodeBlock code={command} language="powershell"/></div>)}</div></Card>
      <aside className="space-y-4"><Card className="p-5"><div className="flex items-center gap-2"><TerminalSquare size={16} className="text-cyan-300"/><h2 className="text-sm font-semibold">Run state</h2></div><div className="mt-5 grid gap-2"><Button onClick={() => transition("start")}><Play size={14}/>Record start</Button><Button variant="secondary" disabled={status === "idle"} onClick={() => transition("test")}><CheckCircle2 size={14}/>Record passing test</Button><Button variant="ghost" onClick={() => transition("reset")}><RotateCcw size={14}/>Reset workspace state</Button></div><div className="mt-5 flex items-center gap-2 rounded-lg border border-white/[.07] bg-white/[.025] p-3 text-[10px] text-slate-400">{status === "idle" ? <CircleStop size={14}/> : <CheckCircle2 size={14} className="text-emerald-300"/>}{status === "idle" ? "Not started" : status === "ready" ? "Started; test evidence pending" : "Started and verified"}</div></Card><Card className="p-5"><div className="text-[10px] text-slate-500">Runtime</div><div className="mt-1 text-sm font-semibold">{lab.runtime}</div><div className="mt-4 text-[10px] text-slate-500">Owned path</div><div className="mt-1 break-all font-mono text-[10px] text-cyan-200">{lab.path}</div><div className="mt-4 text-[10px] text-slate-500">Safety</div><p className="mt-1 text-[10px] leading-relaxed text-slate-400">Offline, resettable, and allowlisted by its checked-in manifest.</p></Card></aside>
    </div>
  </div>;
}
