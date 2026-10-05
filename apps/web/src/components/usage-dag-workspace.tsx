"use client";
import { useEffect, useState } from "react";
import { dagSchema, type UsageDag } from "@/lib/usage-dag";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const nodes = [
  { id: "consume", title: "Consume up to 100 events", detail: "No automatic retry. Durable identity deduplication and broker checkpoint." },
  { id: "validate_parquet", title: "Validate accepted-sink Parquet", detail: "Digest, typed schema, tenant and aggregate lineage. One retry." },
  { id: "refresh_lakehouse", title: "Refresh local Iceberg", detail: "Content-addressed full refresh. One retry; unchanged content skips a snapshot." },
] as const;

export function UsageDagWorkspace() {
  const [data, setData] = useState<UsageDag | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void fetch("/api/pipelines/usage", { cache: "no-store", signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error("Airflow status unavailable or disabled. Inspect the local orchestration runbook.");
      const result = dagSchema.parse(await response.json());
      if (!controller.signal.aborted) { setData(result); setError(""); }
    }).catch(() => { if (!controller.signal.aborted) { setData(null); setError("Airflow status unavailable or disabled. Inspect the local orchestration runbook."); } })
      .finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [refresh]);
  return <section className="space-y-4" aria-label="Usage orchestration">
    <div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-xl font-semibold">Usage orchestration</h2><p className="mt-1 text-xs text-slate-500">Source-owned manual DAG · one active run · tenant-bound, read-only status</p></div><Button disabled={busy} onClick={() => { setBusy(true); setRefresh(value => value + 1); }}>Refresh DAG status</Button></div>
    {busy && <p role="status" className="text-xs text-slate-500">Checking Airflow…</p>}
    {error && <p role="alert" className="text-xs text-rose-300">{error}</p>}
    <ol aria-label="Pipeline dependencies" className="grid gap-3 md:grid-cols-3">{nodes.map((node, index) => {
      const observed = !busy && data?.latest_tasks.find(item => item.task_id === node.id);
      return <li key={node.id}><Card className="h-full p-5"><div className="text-xs text-cyan-300">{index + 1} · {node.id}</div><h3 className="mt-2 text-sm font-semibold">{node.title}</h3><p className="mt-2 text-xs text-slate-500">{node.detail}</p><p className="mt-3 text-xs">{observed ? `${observed.state} · attempt ${observed.try_number}` : "No current task observation"}</p></Card></li>;
    })}</ol>
    <p className="text-xs text-slate-500">Dependencies: consume → validate_parquet → refresh_lakehouse. Each reads current sink state; this is not an atomic broker-cutoff snapshot.</p>
    {!busy && data && <><p className="text-xs text-slate-500">{data.dag_id} · checked <time>{data.checked_at}</time></p>{data.runs.length === 0 ? <p className="text-sm">No Airflow runs returned.</p> : <div className="overflow-x-auto"><table className="w-full text-left text-xs"><caption className="py-2 text-left">Latest five Airflow runs</caption><thead><tr><th className="p-2">Run</th><th className="p-2">State</th><th className="p-2">Started</th><th className="p-2">Ended</th></tr></thead><tbody>{data.runs.map(run => <tr key={run.dag_run_id}><td className="p-2">{run.dag_run_id}</td><td className="p-2">{run.state}</td><td className="p-2">{run.start_date ?? "—"}</td><td className="p-2">{run.end_date ?? "—"}</td></tr>)}</tbody></table></div>}</>}
  </section>;
}
