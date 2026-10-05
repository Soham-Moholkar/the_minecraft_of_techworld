"use client";
import { useEffect, useState } from "react";
import { deploymentReviewSchema, type DeploymentReview } from "@/lib/deployment-review";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

/** A cancelled/failed refresh clears prior evidence instead of implying current health. */
export function DeploymentWorkspace() {
  const [data, setData] = useState<DeploymentReview | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const [revision, setRevision] = useState(0);
  const [showTeardown, setShowTeardown] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    void fetch("/api/infrastructure/deployment", { cache: "no-store", signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error("unavailable");
      const result = deploymentReviewSchema.parse(await response.json());
      if (!controller.signal.aborted) { setData(result); setError(""); }
    }).catch(() => {
      if (!controller.signal.aborted) { setData(null); setError("Deployment review unavailable or disabled. Enable ATLAS_DEPLOYMENT_REVIEW_ENABLED for a trusted local owner and check the deployment-review runbook."); }
    }).finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [revision]);
  const observed = !busy ? data : null;
  return <div className="space-y-5">
    <Card className="space-y-4 p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><h2 className="text-xl font-semibold">Development deployment review</h2><p className="mt-1 text-xs text-slate-500">Release atlas · namespace atlas-dev · Helm 4.3.0</p></div><Button disabled={busy} onClick={() => { setBusy(true); setShowTeardown(false); setRevision(value => value + 1); }}>Refresh deployment review</Button></div>
      {busy && <p role="status">Checking owned manifest…</p>}{error && <p role="alert" className="text-sm text-rose-300">{error}</p>}
      {observed && <><div className="grid gap-3 md:grid-cols-3"><div className="rounded-lg border border-slate-800 p-4"><p className="text-xs text-slate-500">Manifest policy</p><p className={observed.status === "passed" ? "mt-2 font-semibold text-emerald-300" : "mt-2 font-semibold text-rose-300"}>{observed.status === "passed" ? "Local checks passed" : "Deployment review blocked"}</p></div><div className="rounded-lg border border-slate-800 p-4"><p className="text-xs text-slate-500">Live cluster</p><p className="mt-2 font-semibold text-amber-300">Not checked</p></div><div className="rounded-lg border border-slate-800 p-4"><p className="text-xs text-slate-500">Cloud spend</p><p className="mt-2 font-semibold">No cost estimate</p></div></div>
        <p className="text-xs text-slate-500">Observed <time dateTime={observed.checked_at}>{observed.checked_at}</time>. Manifest checks do not prove scheduling, image startup, storage recovery or network policy enforcement.</p><p className="break-all font-mono text-xs text-slate-500">SHA-256 {observed.manifest_digest}</p>
        {observed.findings.length > 0 && <div role="alert" className="rounded-lg border border-rose-900 p-4"><h3 className="font-semibold">Policy findings</h3><ul className="mt-2 space-y-1 text-sm">{observed.findings.map((finding, index) => <li key={`${finding.code}-${index}`}>{finding.message}</li>)}</ul></div>}
      </>}
    </Card>
    {observed && <>
      <Card className="space-y-4 p-5"><h2 className="text-lg font-semibold">Resource budget</h2>{observed.budget ? <><dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{[["CPU request / limit", `${observed.budget.cpu_request_millicores} / ${observed.budget.cpu_limit_millicores} mCPU`], ["Memory request / limit", `${observed.budget.memory_request_mib} / ${observed.budget.memory_limit_mib} MiB`], ["Retained storage", `${observed.budget.storage_mib} MiB`], ["Total replicas", `${observed.budget.replicas}`]].map(([label, value]) => <div key={label}><dt className="text-xs text-slate-500">{label}</dt><dd className="mt-2 font-mono text-sm">{value}</dd></div>)}</dl><p className="text-xs text-slate-500">One API writer and one web pod, Recreate rollout, bounded temporary volumes and a namespace quota. This development topology uses SQLite; availability and recovery require live acceptance.</p></> : <p className="text-sm text-slate-500">Budget withheld until every resource matches the owned contract.</p>}</Card>
      <Card className="space-y-4 p-5"><h2 className="text-lg font-semibold">Owned resources</h2>{observed.resources.length === 0 ? <p>No resource observations returned.</p> : <div className="overflow-x-auto"><table className="w-full text-left text-sm"><caption className="sr-only">Manifest resources and policy results</caption><thead><tr className="border-b border-slate-800 text-xs text-slate-500"><th className="p-2">Resource</th><th className="p-2">Name</th><th className="p-2">Contract</th><th className="p-2">Teardown</th></tr></thead><tbody>{observed.resources.map(resource => <tr key={`${resource.kind}/${resource.name}`} className="border-b border-slate-800/60"><td className="p-2">{resource.kind}</td><td className="p-2 font-mono text-xs">{resource.name}</td><td className="p-2">{resource.matches_contract ? "Matches" : "Review required"}</td><td className="p-2">{resource.retained ? "Retained" : "Remove workload"}</td></tr>)}</tbody></table></div>}</Card>
      <Card className="space-y-4 p-5"><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-lg font-semibold">Teardown review</h2><Button disabled={observed.status !== "passed"} aria-expanded={showTeardown} aria-controls="deployment-teardown" onClick={() => setShowTeardown(value => !value)}>{showTeardown ? "Hide teardown plan" : "Inspect teardown plan"}</Button></div><p className="text-sm text-slate-500">The plan retains the namespace, data volume, operator secret and release metadata. Commands require an operator to verify ownership and context in the terminal.</p><ul className="flex flex-wrap gap-2 text-xs">{observed.retained.map(item => <li key={item} className="rounded border border-slate-800 px-3 py-2">{item}</li>)}</ul>{showTeardown && <div id="deployment-teardown" className="space-y-3"><p className="text-sm text-amber-300">Review only. No command has been executed.</p><pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-xs leading-6">{observed.teardown.join("\n")}</pre></div>}</Card>
    </>}
    <p className="text-xs text-slate-500">Source: infra/helm/atlas · infra/kubernetes · deployment_policy.py · docs/runbooks/deployment-review.md. Change deployment source in the IDE, then render and verify it again.</p>
  </div>;
}
