"use client";

import { useEffect, useState } from "react";
import { lakehouseSchema, streamSchema, type Lakehouse, type UsageStream } from "@/lib/streaming";
import { Button } from "@/components/ui/button";

/** Counter inputs are inert data; tenant, broker and consumer selection are server-owned. */
export function StreamingWorkspace() {
  const [snapshot, setSnapshot] = useState<UsageStream | null>(null);
  const [lakehouse, setLakehouse] = useState<Lakehouse | null>(null);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [eventId, setEventId] = useState("");
  const [units, setUnits] = useState("1");

  async function operate(suffix = "", payload?: object) {
    setBusy(true); setError("");
    try {
      const response = await fetch(`/api/streaming/usage${suffix}`, { method: payload ? "POST" : "GET",
        cache: "no-store", headers: { "Content-Type": "application/json" },
        body: payload ? JSON.stringify(payload) : undefined });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "Stream operation failed.");
      setSnapshot(streamSchema.parse(result));
    } catch (failure) { setError(failure instanceof Error ? failure.message : "Stream unavailable."); }
    finally { setBusy(false); }
  }
  useEffect(() => {
    const controller = new AbortController();
    // Only resolved network state updates the view; cleanup prevents stale mounts.
    void fetch("/api/streaming/usage", { cache: "no-store", signal: controller.signal })
      .then(async (response) => {
        const result = await response.json();
        if (!response.ok) throw new Error(result.detail ?? "Stream unavailable.");
        if (!controller.signal.aborted) setSnapshot(streamSchema.parse(result));
      }).catch((failure) => {
        if (!controller.signal.aborted) setError(failure instanceof Error ? failure.message : "Stream unavailable.");
      }).finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, []);

  async function refreshLakehouse() {
    setBusy(true); setError("");
    try {
      const response = await fetch("/api/streaming/usage/lakehouse", { method: "POST",
        headers: { "Content-Type": "application/json" }, body: "{}", cache: "no-store" });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail ?? "Lakehouse unavailable.");
      setLakehouse(lakehouseSchema.parse(result));
    } catch (failure) { setError(failure instanceof Error ? failure.message : "Lakehouse unavailable."); }
    finally { setBusy(false); }
  }

  return <div className="space-y-6 p-6">
    <header><p className="text-xs text-cyan-400">Data Platform / Streaming</p>
      <h1 className="mt-2 text-2xl font-semibold">Usage event pipeline</h1>
      <p className="mt-2 text-sm text-muted-foreground">Publish bounded synthetic counters, process a batch, and inspect durable consumer lag.</p>
      <p className="mt-2 text-xs text-muted-foreground">Trusted local development. At-least-once delivery with durable identity deduplication. Kafka uses one manually assigned partition; distributed group balancing is pending.</p>
    </header>
    {error && <p role="alert" className="text-sm text-rose-400">{error}</p>}
    <div aria-live="polite" className="text-sm">{busy ? "Loading stream…" : !snapshot ? "No stream snapshot available." : `${snapshot.provider} · ${snapshot.topic} · ${snapshot.consumer}`}</div>
    <div className="flex flex-wrap gap-3"><Button disabled={busy} onClick={() => void operate()}>Refresh</Button>
      <Button disabled={busy || !snapshot} onClick={() => void operate("/consume", { limit: 10 })}>Process up to 10 events</Button></div>
    <form className="flex flex-wrap items-end gap-3" onSubmit={(event) => {
      event.preventDefault(); void operate("/events", { events: [{ event_id: eventId, units: Number(units) }] });
    }}>
      <label className="text-sm">Event ID<input className="mt-1 block rounded border bg-background p-2" required pattern="[a-z][a-z0-9-]{0,47}" maxLength={48} value={eventId} onChange={(e) => setEventId(e.target.value)}/></label>
      <label className="text-sm">Usage units<input className="mt-1 block rounded border bg-background p-2" type="number" required min={-1000} max={1000} step={1} value={units} onChange={(e) => setUnits(e.target.value)}/></label>
      <Button disabled={busy || !snapshot} type="submit">Publish event</Button>
    </form>
    <p className="text-xs text-muted-foreground">Keep the same event ID when retrying an uncertain delivery. Negative units are quarantined during processing.</p>
    {snapshot && <>
      <dl className="flex flex-wrap gap-8 text-sm"><div><dt>Accepted events</dt><dd>{snapshot.accepted}</dd></div><div><dt>Usage total</dt><dd>{snapshot.units}</dd></div><div><dt>Quarantined</dt><dd>{snapshot.quarantined}</dd></div><div><dt>Last batch</dt><dd>{snapshot.processed}</dd></div></dl>
      <div className="overflow-x-auto"><table className="w-full text-left text-sm"><caption className="py-3 text-left">Topic offsets and backpressure (offsets identify the next record)</caption>
        <thead><tr>{["Partition", "Earliest", "End", "Checkpoint", "Lag", "Retention"].map((name) => <th className="p-2" key={name}>{name}</th>)}</tr></thead>
        <tbody>{snapshot.partitions.map((part) => <tr key={part.partition}>{[part.partition, part.earliest, part.end, part.checkpoint, part.lag].map((value, i) => <td className="p-2" key={i}>{value}</td>)}<td className="p-2">{part.retention_gap ? "Gap: processing blocked" : "In range"}</td></tr>)}</tbody>
      </table></div>
      <p className="text-xs text-muted-foreground">Source → validated counter → durable deduplicated sink → broker checkpoint. Quarantine retains reason and offset, never raw rejected payload.</p>
      <a className="inline-block text-sm text-cyan-400 underline" href="/api/streaming/usage/export" download="atlas-usage.parquet">Download accepted events as Parquet</a>
      <p className="text-xs text-muted-foreground">The file embeds tenant, provider, transform, row count and usage total as lineage metadata. Requires the streaming extras. Export reflects a consistent sink read, not a broker offset cutoff.</p>
      <div><Button disabled={busy} onClick={() => void refreshLakehouse()}>Refresh local Iceberg snapshot</Button>
        <p className="mt-2 text-xs text-muted-foreground">Separate lakehouse opt-in. Full accepted-sink refresh, at most 32 snapshots. Identical content creates no new snapshot. This local SQLite catalog does not provide distributed processing.</p></div>
      {lakehouse && <section aria-label="Lakehouse snapshot history"><h2 className="text-lg font-semibold">{lakehouse.table}</h2>
        <p className="text-sm">{lakehouse.rows} rows · {lakehouse.units} units · {lakehouse.changed ? "Published" : "Unchanged"}</p>
        <ul className="mt-2 space-y-1 text-xs">{lakehouse.snapshots.map((item) => <li key={item.snapshot_id}>Snapshot {item.snapshot_id} · {item.operation} · {item.rows} rows</li>)}</ul>
      </section>}
    </>}
  </div>;
}
