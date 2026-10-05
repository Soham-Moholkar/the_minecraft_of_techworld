"use client";
import { useEffect, useState } from "react";
import { flinkSchema, type UsageFlink } from "@/lib/usage-flink";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
export function UsageFlinkWorkspace() {
  const [data, setData] = useState<UsageFlink | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void fetch("/api/pipelines/usage/flink", { cache: "no-store", signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error("unavailable");
      const value = flinkSchema.parse(await response.json());
      if (!controller.signal.aborted) { setData(value); setError(""); }
    }).catch(() => { if (!controller.signal.aborted) { setData(null); setError("Flink observation unavailable, disabled or unconfigured."); } })
      .finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [revision]);
  return <Card className="space-y-4 p-5"><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-semibold">Flink checkpoint and backpressure</h2><Button disabled={busy} onClick={() => { setBusy(true); setRevision(value => value + 1); }}>Refresh Flink observation</Button></div>
    <p className="text-xs text-slate-500">Read-only observations for the operator-configured job. Up to three vertices are projected; deprecated pressure samples remain unavailable.</p>
    {busy && <p role="status">Checking Flink…</p>}{error && <p role="alert" className="text-sm text-rose-300">{error}</p>}
    {!busy && data && <><p>Job state: {data.state}</p><dl className="grid gap-3 sm:grid-cols-3"><div><dt className="text-xs text-slate-500">Completed checkpoints</dt><dd>{data.checkpoints.completed}</dd></div><div><dt className="text-xs text-slate-500">Failed checkpoints</dt><dd>{data.checkpoints.failed}</dd></div><div><dt className="text-xs text-slate-500">Checkpoints in progress</dt><dd>{data.checkpoints.in_progress}</dd></div></dl><ul className="space-y-2 text-xs">{data.vertices.map(vertex => <li key={vertex.vertex_id} className="break-all">{vertex.vertex_id} · {vertex.level ?? "No current pressure sample"}</li>)}</ul><p className="break-all text-xs text-slate-500">Job {data.job_id} · checked <time>{data.checked_at}</time></p></>}
    <p className="text-xs text-slate-500">A completed batch or zero checkpoint count does not verify streaming recovery. The source-owned bounded job and Linux acceptance commands are in the usage-compute runbook.</p>
  </Card>;
}
