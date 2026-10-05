"use client";
import { useEffect, useState } from "react";
import { biSchema, type UsageBi } from "@/lib/usage-bi";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
export function UsageBiWorkspace() {
  const [data, setData] = useState<UsageBi | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void fetch("/api/pipelines/usage/bi", { cache: "no-store", signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error("unavailable");
      const value = biSchema.parse(await response.json());
      if (!controller.signal.aborted) { setData(value); setError(""); }
    }).catch(() => { if (!controller.signal.aborted) { setData(null); setError("Superset observation unavailable, disabled or unconfigured."); } })
      .finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [revision]);
  return <Card className="space-y-4 p-5"><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-semibold">Superset usage dashboard</h2><Button disabled={busy} onClick={() => { setBusy(true); setRevision(value => value + 1); }}>Refresh BI observation</Button></div>
    <p className="text-xs text-slate-500">Accepted counters → bounded aggregate projection → dedicated read-only BI dataset. Dashboard metadata is read with a server-held observer credential.</p>
    {busy && <p role="status">Checking Superset…</p>}{error && <p role="alert" className="text-sm text-rose-300">{error}</p>}
    {!busy && data && <><h3 className="font-semibold">{data.title}</h3><p>{data.published ? "Dashboard published" : "Dashboard unpublished"}</p><p className="text-xs text-slate-500">Dashboard {data.dashboard_id} · checked <time>{data.checked_at}</time></p></>}
    <p className="text-xs text-slate-500">Publication does not certify dataset freshness. The operator projection and dashboard setup are described in the usage-BI runbook.</p>
  </Card>;
}
