"use client";
import { useEffect, useState } from "react";
import { infrastructurePlanSchema, type InfrastructurePlan } from "@/lib/infrastructure-plan";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

/** Plan receipt observation grants no execution or cloud provisioning authority. */
export function InfrastructurePlanWorkspace() {
  const [data, setData] = useState<InfrastructurePlan | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void fetch("/api/infrastructure/plan", { cache:"no-store", signal:controller.signal }).then(async response => {
      if (!response.ok) throw new Error("unavailable");
      const result = infrastructurePlanSchema.parse(await response.json());
      if (!controller.signal.aborted) { setData(result); setError(""); }
    }).catch(() => {
      if (!controller.signal.aborted) { setData(null); setError("Local plan observation unavailable or disabled. Enable the independent infrastructure plan opt-in and inspect the local-plan runbook."); }
    }).finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [revision]);
  const observation = !busy ? data : null;
  const receipt = observation?.receipt;
  return <Card className="space-y-4 p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-lg font-semibold">Local infrastructure plan</h2><p className="mt-1 text-xs text-slate-500">OpenTofu 1.13.0 · source-bound budget metadata</p></div><Button disabled={busy} onClick={() => { setBusy(true); setRevision(value => value + 1); }}>Refresh local plan</Button></div>
    <p className="text-sm text-slate-500">Review an actual native plan against an empty disposable state. The planned creation is a local budget record; it provisions no cluster or cloud resource.</p>
    {busy && <p role="status">Checking local plan receipt…</p>}{error && <p role="alert" className="text-sm text-rose-300">{error}</p>}
    {observation && !receipt && <p>No local plan receipt recorded. Run the owned plan verifier from the operator terminal.</p>}
    {receipt && <><p className={observation?.source_current ? "font-medium text-emerald-300" : "font-medium text-amber-300"}>{observation?.source_current ? "Matches current deployment source" : "Deployment source has changed since this plan"}</p><dl className="grid gap-4 sm:grid-cols-3">{[["Create metadata", receipt.created], ["Change", receipt.changed], ["Destroy", receipt.destroyed]].map(([label,value]) => <div key={label}><dt className="text-xs text-slate-500">{label}</dt><dd className="mt-2 text-2xl font-semibold">{value}</dd></div>)}</dl><p className="text-xs text-slate-500">Plan captured <time dateTime={receipt.finished_at}>{receipt.finished_at}</time> · observation <time dateTime={observation?.checked_at}>{observation?.checked_at}</time></p><p className="break-all font-mono text-xs text-slate-500">Plan SHA-256 {receipt.plan_digest}</p><p className="break-all font-mono text-xs text-slate-500">Configuration SHA-256 {receipt.configuration_digest}</p><p className="break-all font-mono text-xs text-slate-500">Manifest SHA-256 {receipt.input.manifest_digest}</p></>}
    <p className="text-xs text-slate-500">Receipt only. Binary plans, state, credentials and provider values are not served. Native verification exercises local idempotence, budget rejection and owned cleanup; apply remains outside the application.</p>
  </Card>;
}
