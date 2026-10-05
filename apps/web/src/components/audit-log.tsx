"use client";

import { useEffect, useState } from "react";
import { FileKey2, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

type AuditEvent = {
  id: string;
  actor: string;
  action: string;
  target_type: string;
  target_id: string;
  details: Record<string, string>;
  created_at: string;
};

export function AuditLog() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "error">("loading");
  useEffect(() => {
    let active = true;
    void fetch("/api/audit")
      .then(async (response) => {
        if (!response.ok) throw new Error("audit unavailable");
        const data = await response.json() as AuditEvent[];
        if (active) { setEvents(data); setState("ready"); }
      })
      .catch(() => { if (active) setState("error"); });
    return () => { active = false; };
  }, []);

  return <Card className="overflow-hidden"><div className="flex items-center justify-between border-b border-white/[.07] px-5 py-4"><div><h2 className="text-sm font-semibold">Tenant audit trail</h2><p className="mt-1 text-[10px] text-slate-500">Immutable evidence committed with sensitive mutations</p></div><FileKey2 size={16} className="text-cyan-300"/></div>{state === "loading" && <div className="p-8 text-center text-xs text-slate-500">Loading audit evidence…</div>}{state === "error" && <div role="alert" className="p-8 text-center text-xs text-rose-300">Audit provider unavailable.</div>}{state === "ready" && events.length === 0 && <div className="p-8 text-center text-xs text-slate-500">No sensitive mutations have occurred since the audit migration.</div>}{events.map((event)=><div key={event.id} className="grid gap-3 border-b border-white/[.06] px-5 py-4 last:border-0 sm:grid-cols-[32px_1fr_auto]"><div className="grid size-8 place-items-center rounded-lg bg-emerald-400/[.07] text-emerald-300"><ShieldCheck size={15}/></div><div><div className="text-xs font-semibold">{event.action}</div><div className="mt-1 text-[10px] text-slate-500">{event.actor} · {event.target_type}/{event.target_id.slice(0,8)}</div><div className="mt-2 flex flex-wrap gap-1">{Object.entries(event.details).map(([key,value])=><Badge key={key} tone="neutral">{key}: {value}</Badge>)}</div></div><time className="text-[9px] text-slate-600">{new Date(event.created_at).toLocaleString()}</time></div>)}</Card>;
}

