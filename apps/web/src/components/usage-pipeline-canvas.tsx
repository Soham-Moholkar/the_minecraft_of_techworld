"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { z } from "zod";
import { streamSchema, type UsageStream } from "@/lib/streaming";
import { computeSchema, type UsageCompute } from "@/lib/usage-compute";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const stages = [
  { id: "topic", name: "Usage topic", source: "apps/api-python/src/atlas_api/streaming.py", detail: "Published counters wait for the configured consumer. Lag and retention observations come from the broker." },
  { id: "sink", name: "Accepted sink", source: "apps/api-python/src/atlas_api/streaming.py", detail: "Validated identities commit to the durable sink before broker acknowledgement. Replays deduplicate; rejected records retain only reason and offset." },
  { id: "parquet", name: "Typed Parquet", source: "apps/api-python/src/atlas_api/streaming_export.py", detail: "A consistent accepted-sink export embeds tenant, provider, transform, aggregates and SHA-256 lineage. Separate exports may observe later events." },
  { id: "spark", name: "Spark rollup", source: "infra/spark/usage_job.py", detail: "The operator job validates Parquet lineage, runs actual Spark SQL and publishes a numeric receipt. Source currency is checked independently on each observation." },
  { id: "iceberg", name: "Iceberg snapshots", source: "apps/api-python/src/atlas_api/usage_lakehouse.py", detail: "An explicit refresh projects accepted events into local Iceberg. Identical content skips a snapshot. Inspect actual snapshot history in Usage streaming." },
  { id: "flink", name: "Flink batch", source: "infra/flink/usage_job.py", detail: "The source-owned batch alternative validates the same Parquet contract. The separate fixed-job observation below reports actual checkpoint and pressure metadata when configured." },
  { id: "bi", name: "BI projection", source: "scripts/publish_usage_bi.py", detail: "The operator publisher replaces one aggregate-only SQLite row. Superset receives a read-only dataset; dashboard publication does not certify freshness." },
] as const;
type StageId = typeof stages[number]["id"];
type Evidence<T> = { state: "checking" | "available" | "unavailable"; value: T | null };
const checking = { state: "checking", value: null } as const;

async function observe<T>(path: string, schema: z.ZodType<T>, signal: AbortSignal): Promise<Evidence<T>> {
  try {
    const response = await fetch(path, { cache: "no-store", signal });
    if (!response.ok) throw new Error("unavailable");
    return { state: "available", value: schema.parse(await response.json()) };
  } catch {
    return { state: "unavailable", value: null };
  }
}

/** Source topology is fixed; observations never submit jobs or refresh snapshots. */
export function UsagePipelineCanvas() {
  const [selected, setSelected] = useState<StageId>("sink");
  const [revision, setRevision] = useState(0);
  const [stream, setStream] = useState<Evidence<UsageStream>>(checking);
  const [compute, setCompute] = useState<Evidence<UsageCompute>>(checking);
  useEffect(() => {
    const controller = new AbortController();
    // Independent branches settle independently. A disabled compute provider
    // cannot hide real broker observations, and old mounts never update state.
    void observe("/api/streaming/usage", streamSchema, controller.signal).then(value => {
      if (!controller.signal.aborted) setStream(value);
    });
    void observe("/api/pipelines/usage/compute", computeSchema, controller.signal).then(value => {
      if (!controller.signal.aborted) setCompute(value);
    });
    return () => controller.abort();
  }, [revision]);
  const stage = stages.find(value => value.id === selected)!;
  const busy = stream.state === "checking" || compute.state === "checking";
  const lag = stream.value?.partitions.reduce((total, part) => total + part.lag, 0);
  function label(id: StageId) {
    if (id === "topic" || id === "sink") return stream.state === "available" ? "Observed" : stream.state === "checking" ? "Checking…" : "Observation unavailable";
    if (id === "spark") return compute.state === "checking" ? "Checking…" : !compute.value ? "Observation unavailable" : !compute.value.receipt ? "No receipt" : compute.value.source_current ? "Current receipt" : "Older source receipt";
    return "Source-defined branch";
  }
  return <Card className="space-y-5 p-5">
    <div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-semibold">Usage pipeline canvas</h2><Button disabled={busy} onClick={() => { setStream(checking); setCompute(checking); setRevision(value => value + 1); }}>Refresh canvas evidence</Button></div>
    <p className="text-sm text-slate-400">Select a stage to inspect its boundary and evidence. Arrows show the source-defined data flow; observations are separate reads rather than one atomic pipeline snapshot.</p>
    <div aria-label="Usage data flow" className="grid gap-3 md:grid-cols-3">
      <div className="space-y-3"><StageButton stage={stages[0]} selected={selected} select={setSelected} label={label("topic")}/><p className="text-center text-cyan-300">Validate and deduplicate ↓</p><StageButton stage={stages[1]} selected={selected} select={setSelected} label={label("sink")}/><p className="text-center text-cyan-300">Accepted data →</p></div>
      <div className="space-y-3"><StageButton stage={stages[2]} selected={selected} select={setSelected} label={label("parquet")}/><p className="text-center text-cyan-300">Export branches →</p></div>
      <div className="space-y-3">{stages.slice(3).map(value => <StageButton key={value.id} stage={value} selected={selected} select={setSelected} label={label(value.id)}/>)}</div>
    </div>
    <section aria-label="Selected pipeline stage" className="space-y-3 rounded-lg border border-slate-800 p-4">
      <h3 className="font-semibold">{stage.name}</h3><p className="text-sm text-slate-400">{stage.detail}</p>
      {(selected === "topic" || selected === "sink") && (stream.state === "checking" ? <p role="status">Checking streaming evidence…</p> : !stream.value ? <p>Streaming evidence unavailable or disabled.</p> : selected === "topic" ? <><p className="break-all">{stream.value.provider} · {stream.value.topic}</p><p>Consumer lag: {lag} · {stream.value.partitions.some(part => part.retention_gap) ? "Retention gap: processing blocked" : "Offsets in range"}</p></> : <p>{stream.value.accepted} accepted events · {stream.value.units} usage units · {stream.value.quarantined} quarantined</p>)}
      {selected === "spark" && (compute.state === "checking" ? <p role="status">Checking compute evidence…</p> : !compute.value ? <p>Compute evidence unavailable or disabled.</p> : !compute.value.receipt ? <p>No Spark receipt recorded.</p> : <><p>{compute.value.source_current ? "Receipt matches current accepted data" : "Receipt belongs to an older source"}</p><p>{compute.value.receipt.rows} rows · {compute.value.receipt.units} units · {compute.value.receipt.mode}</p><p className="break-all text-xs">Export SHA-256: {compute.value.receipt.source_digest}</p><p className="text-xs">Checked <time>{compute.value.checked_at}</time></p></>)}
      {selected === "parquet" && <p className="text-sm">Inspect the receipt’s export digest by selecting Spark. A digest from an older job is historical evidence.</p>}
      <p className="break-all text-xs text-slate-500">Owned source: {stage.source}</p>
    </section>
    <p className="text-xs text-slate-500">Airflow orchestrates consume → Parquet validation → Iceberg refresh; its actual run/task observations are below. Flink and BI observations are independent branches. Selecting or refreshing this canvas performs reads only.</p>
    <Link className="text-sm text-cyan-300 underline" href="/streaming">Inspect streaming offsets and publish snapshots</Link>
  </Card>;
}

function StageButton({ stage, selected, select, label }: { stage: typeof stages[number]; selected: StageId; select: (id: StageId) => void; label: string }) {
  return <button type="button" aria-pressed={selected === stage.id} onClick={() => select(stage.id)} className={`w-full rounded-lg border p-3 text-left focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 ${selected === stage.id ? "border-cyan-400 bg-cyan-950/30" : "border-slate-800 bg-slate-950/30"}`}><span className="block font-medium">{stage.name}</span><span className="text-xs text-slate-400">{label}</span></button>;
}
