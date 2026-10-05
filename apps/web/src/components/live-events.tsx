"use client";

import { useEffect, useState } from "react";
import { RadioTower, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

type AuditEvent = {
  id: string;
  actor: string;
  action: string;
  target_type: string;
  target_id: string;
  created_at: string;
};

export function LiveEvents() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [connection, setConnection] = useState<"connecting" | "live" | "retrying">("connecting");

  useEffect(() => {
    // EventSource owns reconnect/backoff and automatically sends the latest SSE id
    // as Last-Event-ID; the BFF forwards it without exposing server credentials.
    const source = new EventSource("/api/events");
    source.onopen = () => setConnection("live");
    source.onerror = () => setConnection("retrying");
    source.addEventListener("audit", (message) => {
      const event = JSON.parse((message as MessageEvent<string>).data) as AuditEvent;
      setEvents((current) => [event, ...current.filter((item) => item.id !== event.id)].slice(0, 12));
    });
    return () => source.close();
  }, []);

  return <Card className="overflow-hidden"><div className="flex items-center justify-between border-b border-white/[.07] px-5 py-4"><div><h2 className="text-sm font-semibold">Live control-plane events</h2><p className="mt-1 text-[10px] text-slate-500">Authenticated Server-Sent Events through the BFF</p></div><Badge tone={connection === "live" ? "success" : connection === "retrying" ? "warning" : "neutral"}><RadioTower size={11}/>{connection}</Badge></div>{events.length === 0 ? <div className="p-8 text-center text-xs text-slate-500">Waiting for tenant-visible events…</div> : <div>{events.map((event) => <div key={event.id} className="flex items-center gap-3 border-b border-white/[.06] px-5 py-3 last:border-0"><div className="grid size-8 place-items-center rounded-lg bg-cyan-300/[.07] text-cyan-300"><ShieldCheck size={14}/></div><div className="min-w-0 flex-1"><div className="text-xs font-semibold">{event.action}</div><div className="mt-1 truncate text-[10px] text-slate-500">{event.actor} · {event.target_type}/{event.target_id.slice(0, 8)}</div></div><time className="text-[9px] text-slate-600">{new Date(event.created_at).toLocaleTimeString()}</time></div>)}</div>}</Card>;
}
