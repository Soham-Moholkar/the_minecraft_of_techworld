"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { z } from "zod";
import { ArrowRight, GitBranch, ShieldCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { auditSchema, healthSchema, projectPageSchema } from "@/lib/control-plane";
import snapshot from "@/data/quality-snapshot.json";

type Load<T> = { state: "loading" } | { state: "error" } | { state: "ready"; data: T; checked: string };
function useSnapshot<T>(url: string, schema: z.ZodType<T>): Load<T> {
  const [result, setResult] = useState<Load<T>>({ state: "loading" });
  useEffect(() => {
    const controller = new AbortController();
    void fetch(url, { cache: "no-store", signal: controller.signal }).then(async (response) => {
      if (!response.ok) throw new Error("provider unavailable");
      const data = schema.parse(await response.json());
      if (!controller.signal.aborted) setResult({ state: "ready", data, checked: new Date().toISOString() });
    }).catch(() => { if (!controller.signal.aborted) setResult({ state: "error" }); });
    return () => controller.abort();
  }, [url, schema]);
  return result;
}

/** Each dependency fails independently; a readiness read is never an uptime SLO. */
export function Dashboard() {
  const health = useSnapshot("/api/health", healthSchema);
  const projects = useSnapshot("/api/projects", projectPageSchema);
  const audit = useSnapshot("/api/audit", auditSchema);
  return <div className="space-y-6">
    <section className="border-b border-white/[.07] pb-6"><div className="text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300">Operations overview</div><h1 className="mt-2 text-3xl font-semibold">Workspace overview</h1><p className="mt-2 text-sm text-slate-500">Current control-plane responses and recorded quality evidence.</p></section>
    <section aria-label="Control plane indicators" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <Card className="p-5"><h2 className="text-xs text-slate-500">API readiness</h2><div className="mt-3 text-xl font-semibold">{health.state === "ready" ? health.data.status : health.state === "error" ? "Unavailable" : "Checking…"}</div>{health.state === "ready" && <p className="mt-2 text-xs text-slate-500">Version {health.data.version} · checked <time>{health.checked}</time></p>}</Card>
      <Card className="p-5"><h2 className="text-xs text-slate-500">Database readiness</h2><div className="mt-3 text-xl font-semibold">{health.state === "ready" ? health.data.database : health.state === "error" ? "Unknown" : "Checking…"}</div></Card>
      <Card className="p-5"><h2 className="text-xs text-slate-500">Tenant projects</h2><div className="mt-3 text-xl font-semibold">{projects.state === "ready" ? projects.data.total : projects.state === "error" ? "Unavailable" : "Loading…"}</div></Card>
      <Card className="p-5"><h2 className="text-xs text-slate-500">Recorded quality gates</h2><div className="mt-3 text-xl font-semibold">{snapshot.summary.passed}/{snapshot.summary.total} passed</div><p className="mt-2 text-xs text-slate-500">Recorded <time>{snapshot.generated_at}</time></p><Link href="/tests" className="mt-3 inline-block text-xs text-cyan-300">Inspect evidence</Link></Card>
    </section>
    <section className="grid gap-5 xl:grid-cols-2">
      <Card className="overflow-hidden"><div className="border-b border-white/[.07] p-5"><h2 className="text-sm font-semibold">Persisted projects</h2><Link href="/projects" className="text-xs text-cyan-300">All projects</Link></div>
        {projects.state === "loading" && <p className="p-5 text-xs text-slate-500">Loading project inventory…</p>}
        {projects.state === "error" && <p role="alert" className="p-5 text-xs text-rose-300">Project inventory unavailable.</p>}
        {projects.state === "ready" && (projects.data.items.length === 0 ? <p className="p-5 text-xs text-slate-500">No projects yet.</p> : projects.data.items.slice(0, 3).map((project) => <div key={project.id} className="flex items-center gap-3 border-b border-white/[.06] p-5"><GitBranch size={16} className="text-cyan-300"/><div className="min-w-0 flex-1"><div className="text-xs font-medium">{project.name}</div><p className="truncate text-xs text-slate-500">{project.description}</p></div><Badge tone="neutral">{project.status}</Badge></div>))}
      </Card>
      <Card className="overflow-hidden"><div className="border-b border-white/[.07] p-5"><h2 className="text-sm font-semibold">Recent tenant audit events</h2><p className="text-xs text-slate-500">Latest bounded page of committed mutation evidence.</p></div>
        {audit.state === "loading" && <p className="p-5 text-xs text-slate-500">Loading audit evidence…</p>}
        {audit.state === "error" && <p role="alert" className="p-5 text-xs text-rose-300">Audit provider unavailable.</p>}
        {audit.state === "ready" && (audit.data.length === 0 ? <p className="p-5 text-xs text-slate-500">No audit events returned.</p> : audit.data.slice(0, 4).map((event) => <div key={event.id} className="flex gap-3 border-b border-white/[.06] p-5"><ShieldCheck size={16} className="text-cyan-300"/><div><div className="text-xs font-medium">{event.action}</div><p className="mt-1 text-xs text-slate-500">{event.actor} · <time>{event.created_at}</time></p></div></div>))}
      </Card>
    </section>
    <section className="grid gap-3 md:grid-cols-3">{[
      ["/streaming", "Usage streaming", "Publish, process and inspect actual offsets and lakehouse snapshots."],
      ["/developer/technologies", "Engineering progression", "Implemented levels, source paths and verification commands."],
      ["/observability", "Service diagnostics", "Inspect health and request telemetry."],
    ].map(([href, title, detail]) => <Link href={href} key={href}><Card className="h-full p-5"><h2 className="text-sm font-semibold">{title}</h2><p className="mt-2 text-xs text-slate-500">{detail}</p><div className="mt-4 flex items-center gap-1 text-xs text-cyan-300">Open <ArrowRight size={12}/></div></Card></Link>)}</section>
  </div>;
}
