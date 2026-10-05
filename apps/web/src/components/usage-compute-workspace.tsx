"use client";
import { useEffect, useState } from "react";
import { computeSchema, type UsageCompute } from "@/lib/usage-compute";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

/** Local worker receipts are observations, not a remote execution attestation. */
export function UsageComputeWorkspace() {
  const [data, setData] = useState<UsageCompute | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void fetch("/api/pipelines/usage/compute", { cache: "no-store", signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error("unavailable");
      const value = computeSchema.parse(await response.json());
      if (!controller.signal.aborted) { setData(value); setError(""); }
    }).catch(() => { if (!controller.signal.aborted) { setData(null); setError("Spark observation unavailable or disabled. Inspect the usage-compute runbook."); } })
      .finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [revision]);
  const receipt = !busy && data?.receipt;
  return <Card className="space-y-4 p-5"><div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-semibold">Spark usage rollup</h2><Button disabled={busy} onClick={() => { setBusy(true); setRevision(value => value + 1); }}>Refresh compute observation</Button></div>
    <p className="text-xs text-slate-500">Accepted sink → authenticated Parquet export → typed Spark aggregation → content-bound local receipt. Run the source-owned job from the operator terminal.</p>
    {busy && <p role="status">Checking compute observation…</p>}{error && <p role="alert" className="text-sm text-rose-300">{error}</p>}
    {!busy && data && !data.receipt && <p>No Spark receipt recorded for this tenant and provider.</p>}
    {receipt && <><p>{data?.source_current ? "Matches current accepted data" : "Source has changed since this job"}</p><dl className="grid gap-3 sm:grid-cols-4"><div><dt className="text-xs text-slate-500">Rows</dt><dd>{receipt.rows}</dd></div><div><dt className="text-xs text-slate-500">Usage units</dt><dd>{receipt.units}</dd></div><div><dt className="text-xs text-slate-500">Execution mode</dt><dd>{receipt.mode}</dd></div><div><dt className="text-xs text-slate-500">Input partitions</dt><dd>{receipt.partitions}</dd></div></dl><p className="break-all text-xs text-slate-500">Source SHA-256: {receipt.source_digest}</p><p className="text-xs text-slate-500">Spark {receipt.version} · completed <time>{receipt.finished_at}</time> · {receipt.duration_ms} ms</p></>}
    <p className="text-xs text-slate-500">The shared directory is an operator trust boundary. This receipt does not certify cluster health or end-to-end exactly-once delivery.</p>
  </Card>;
}
