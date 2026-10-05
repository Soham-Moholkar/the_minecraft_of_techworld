"use client";

import Link from "next/link";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { datasetListSchema, datasetSchema, sampleCsv, type Dataset, type DatasetSummary } from "@/lib/datasets";

async function readResponse(response: Response): Promise<unknown> {
  const body: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string"
      ? body.detail : "Dataset request failed.";
    throw new Error(detail);
  }
  return body;
}

export function DatasetWorkspace() {
  const [catalog, setCatalog] = useState<DatasetSummary[]>([]);
  const [selected, setSelected] = useState<Dataset | null>(null);
  const [name, setName] = useState("Service usage sample");
  const [csv, setCsv] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const selection = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    void fetch("/api/datasets", { cache: "no-store", signal: controller.signal })
      .then(readResponse).then((body) => setCatalog(datasetListSchema.parse(body)))
      .catch((reason: unknown) => { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Catalog unavailable."); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => { controller.abort(); selection.current?.abort(); };
  }, []);

  async function inspect(id: string) {
    selection.current?.abort();
    const controller = new AbortController();
    selection.current = controller;
    setError("");
    setSelected(null);
    setLoading(true);
    try {
      const body = await readResponse(await fetch(`/api/datasets?id=${id}`, { cache: "no-store", signal: controller.signal }));
      if (!controller.signal.aborted) setSelected(datasetSchema.parse(body));
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Dataset unavailable.");
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }

  async function importCsv(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    selection.current?.abort();
    setLoading(false);
    setBusy(true);
    setError("");
    try {
      const body = await readResponse(await fetch("/api/datasets", { method: "POST",
        headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, csv_text: csv }) }));
      const dataset = datasetSchema.parse(body);
      setSelected(dataset);
      setCatalog((current) => [dataset, ...current]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Import failed.");
    } finally { setBusy(false); }
  }

  const profile = selected?.profile;
  const field = "mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm text-slate-100 focus-visible:outline-2 focus-visible:outline-cyan-400";
  return <div className="space-y-6">
    <header><p className="text-xs uppercase tracking-widest text-cyan-300">Data platform · Phase 5</p>
      <h1 className="mt-2 text-3xl font-semibold">Dataset catalog</h1>
      <p className="mt-2 max-w-3xl text-sm text-slate-400">Import operational measurements, inspect quality, and compare aggregation engines. Profiles and cleaned rows persist in your workspace.</p>
    </header>
    {error ? <p role="alert" className="rounded-lg border border-rose-400/30 p-4 text-sm text-rose-200">{error}</p> : null}
    <div className="grid gap-6 xl:grid-cols-[1fr_1.3fr]">
      <Card className="min-w-0 p-5"><h2 className="text-lg font-semibold">Import and profile</h2>
        <p className="mt-2 text-xs text-slate-400">CSV header: date,service,cost,requests. ISO dates, finite nonnegative costs, integer requests. Maximum 5,000 rows and 256 KiB.</p>
        <form onSubmit={importCsv} className="mt-4 space-y-4">
          <label className="block text-xs text-slate-300">Dataset name<input required minLength={2} maxLength={120} className={field} value={name} onChange={(event) => setName(event.target.value)} /></label>
          <label className="block text-xs text-slate-300">Measurement CSV<textarea required maxLength={262144} rows={8} className={`${field} font-mono text-xs`} value={csv} onChange={(event) => setCsv(event.target.value)} /></label>
          <div className="flex flex-wrap gap-3"><Button type="button" variant="secondary" disabled={busy} onClick={() => setCsv(sampleCsv)}>Load sample CSV</Button>
            <Button type="submit" disabled={busy || loading}>{busy ? "Profiling…" : "Import dataset"}</Button></div>
          {busy ? <p role="status" className="text-xs text-cyan-200">Cleaning data and checking three engines…</p> : null}
        </form>
      </Card>
      <Card className="min-w-0 p-5"><h2 className="text-lg font-semibold">Saved datasets</h2>
        {loading ? <p role="status" className="mt-4 text-sm text-slate-400">Loading dataset evidence…</p> : null}
        {!loading && catalog.length === 0 ? <p className="mt-4 text-sm text-slate-400">No datasets yet. Import a CSV to create the first profile.</p> : null}
        <ul className="mt-4 max-h-80 space-y-2 overflow-y-auto">{catalog.map((item) => <li key={item.id}>
          <button type="button" disabled={busy} onClick={() => void inspect(item.id)} className="flex w-full items-center justify-between gap-3 rounded-lg border border-white/10 p-3 text-left text-sm hover:bg-white/5 focus-visible:outline-2 focus-visible:outline-cyan-400">
            <span className="break-all">{item.name}</span><Badge>{item.valid_rows} rows</Badge>
          </button></li>)}</ul>
        <Link className="mt-5 inline-block text-xs text-cyan-300" href="/labs/data-science-quality">Open the dirty-data and scaling lab →</Link>
      </Card>
    </div>
    {profile && selected ? <section aria-label="Dataset profile" className="space-y-6">
      <div><h2 className="text-xl font-semibold">{selected.name} · quality profile</h2><p className="mt-2 break-all font-mono text-[10px] text-slate-400">Source SHA-256: {selected.source_checksum}</p></div>
      <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">{[
        ["Input rows", profile.input_rows], ["Valid rows", profile.valid_rows],
        ["Invalid rows excluded", profile.invalid_rows], ["Duplicates removed", profile.duplicate_rows],
      ].map(([label, value]) => <Card className="p-4" key={label}><dt className="text-xs text-slate-400">{label}</dt><dd className="mt-2 text-2xl">{value}</dd></Card>)}</dl>
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="min-w-0 p-5"><h3 className="font-semibold">Cost distribution · NumPy</h3>
          <p className="mt-2 text-xs text-slate-400">Mean {profile.cost_mean.toFixed(2)} · Median {profile.cost_median.toFixed(2)} · p95 {profile.cost_p95.toFixed(2)} · SD {profile.cost_stddev.toFixed(2)}</p>
          <div role="img" aria-label={`Cost histogram across ${profile.valid_rows} cleaned measurements`} className="mt-5 flex h-32 items-end gap-1 border-b border-white/20">
            {profile.histogram.map((bin, index) => <div key={index} title={`${bin.lower.toFixed(2)}–${bin.upper.toFixed(2)}: ${bin.count}`} className="min-w-0 flex-1 bg-cyan-400/70" style={{ height: `${100 * bin.count / Math.max(1, ...profile.histogram.map((item) => item.count))}%` }} />)}
          </div>
          <details className="mt-3 text-xs text-slate-400"><summary className="cursor-pointer">Histogram values</summary><ul>{profile.histogram.map((bin, index) => <li key={index}>{bin.lower.toFixed(2)}–{bin.upper.toFixed(2)}: {bin.count} rows</li>)}</ul></details>
          <p className="mt-4 text-xs text-slate-300">SciPy 95% mean interval: {profile.mean_ci95 ? profile.mean_ci95.map((value) => value.toFixed(2)).join(" to ") : "Not estimated for one observation"}.</p>
        </Card>
        <Card className="min-w-0 overflow-x-auto p-5"><table className="w-full text-left text-xs"><caption className="mb-4 text-left font-semibold text-sm">Cleaned service aggregates</caption><thead><tr><th className="p-2">Service</th><th className="p-2">Cost</th><th className="p-2">Requests</th></tr></thead>
          <tbody>{profile.services.map((item) => <tr key={item.service} className="border-t border-white/10"><th scope="row" className="p-2">{item.service}</th><td className="p-2">{item.cost.toFixed(2)}</td><td className="p-2">{item.requests.toLocaleString()}</td></tr>)}</tbody></table></Card>
      </div>
      <Card className="overflow-x-auto p-5"><table className="w-full text-left text-xs"><caption className="mb-4 text-left text-sm font-semibold">Engine comparison · identical results required</caption><thead><tr>{["Engine", "Version", "p50 (ms)", "p95 (ms)", "Correctness"].map((label) => <th key={label} className="p-2">{label}</th>)}</tr></thead><tbody>
        {profile.engines.map((engine) => <tr key={engine.engine} className="border-t border-white/10"><th scope="row" className="p-2">{engine.engine}</th><td className="p-2">{engine.version}</td><td className="p-2">{engine.p50_ms.toFixed(3)}</td><td className="p-2">{engine.p95_ms.toFixed(3)}</td><td className="p-2">{engine.matches_reference ? "Matched" : "Mismatch"}</td></tr>)}</tbody></table>
        <ul className="mt-5 space-y-2 text-xs text-slate-400">{profile.caveats.map((note) => <li key={note}>{note}</li>)}</ul>
      </Card>
    </section> : null}
  </div>;
}
