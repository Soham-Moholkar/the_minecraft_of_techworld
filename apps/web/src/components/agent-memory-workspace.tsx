"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  memoryReadSchema, memoryRemovalSchema, memorySnapshotSchema, type MemorySnapshot,
} from "@/lib/agent-memory";

async function payload(response: Response): Promise<unknown> {
  const data: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof data === "object" && data !== null && "detail" in data
      && typeof data.detail === "string" ? data.detail : "Memory request failed.";
    throw new Error(detail);
  }
  return data;
}

/** Plain operator notes are never implicitly injected into a model or tool call. */
export function AgentMemoryWorkspace() {
  const [snapshot, setSnapshot] = useState<MemorySnapshot | null>(null);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [provenance, setProvenance] = useState("");
  const [days, setDays] = useState(7);
  const [attested, setAttested] = useState(false);
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [revision, setRevision] = useState(0);
  const [deleteId, setDeleteId] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    async function load() {
      try {
        const response = await fetch("/api/ai/repository/memory", { cache: "no-store", signal: controller.signal });
        const result = memorySnapshotSchema.parse(await payload(response));
        if (active) setSnapshot(result);
      } catch {
        if (active) setError("Operator memory is unavailable. Check the local API, migrations and owner access.");
      } finally {
        if (active) setBusy(false);
      }
    }
    void load();
    // Ignore/abort obsolete reads; the component never polls or persists draft text.
    return () => { active = false; controller.abort(); };
  }, [revision]);

  useEffect(() => {
    if (!snapshot?.items.length) return;
    const earliest = Math.min(...snapshot.items.map((item) => Date.parse(item.expires_at)));
    // Drop expired text from the displayed snapshot without polling the API or
    // changing storage. Cap long timers to avoid the browser's 32-bit overflow.
    const timer = setTimeout(() => setSnapshot((previous) => {
      if (!previous) return previous;
      const items = previous.items.filter((item) => Date.parse(item.expires_at) > Date.now());
      return { ...previous, items, expired_count: previous.expired_count + previous.items.length - items.length };
    }), Math.max(1, Math.min(2_147_483_647, earliest - Date.now() + 1)));
    return () => clearTimeout(timer);
  }, [snapshot]);

  function refresh() {
    setSnapshot(null);
    setError("");
    setDeleteId("");
    setBusy(true);
    setRevision((value) => value + 1);
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!attested || busy || !snapshot) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const response = await fetch("/api/ai/repository/memory", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, content, provenance, retention_days: days, confirmation: "NO SECRETS OR APPROVALS" }),
      });
      memoryReadSchema.parse(await payload(response));
      setTitle(""); setContent(""); setProvenance(""); setAttested(false);
      setNotice("Memory saved. It is not part of model context.");
      refresh();
    } catch (cause) {
      // Failed drafts remain only in component state so the operator can correct them.
      setError(cause instanceof Error ? cause.message : "Memory could not be saved.");
      setBusy(false);
    }
  }

  async function remove(expired: boolean) {
    if (busy || (!expired && !deleteId)) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const response = await fetch(expired ? "/api/ai/repository/memory/purge-expired" : `/api/ai/repository/memory/${deleteId}`, {
        method: expired ? "POST" : "DELETE", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ confirmation: expired ? "REMOVE EXPIRED MEMORY" : "DELETE MEMORY" }),
      });
      const result = memoryRemovalSchema.parse(await payload(response));
      setNotice(`${result.removed_count} memory note(s) physically removed. Audit retains metadata only.`);
      refresh();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Memory could not be removed.");
      setBusy(false);
    }
  }

  return <Card className="mt-6 space-y-4 p-5" aria-label="Operator agent memory">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div><h2 className="text-lg font-semibold">Operator agent memory</h2>
        <p className="text-sm text-slate-400">Tenant-owned notes · maximum 50 · explicit expiry</p></div>
      <Badge>Automatic context disabled</Badge>
      <Button variant="secondary" disabled={busy} onClick={refresh}>Refresh memory</Button>
    </div>
    <p className="text-sm text-slate-300">Do not store credentials, approval digests or personal/confidential data.
      Credential detection is best-effort. Notes are untrusted text and never grant authority or enter model context automatically.
      Expired notes are hidden immediately and physically removed on the next save or explicit cleanup; backups may retain earlier copies.</p>
    {busy && <p role="status">Loading or updating memory…</p>}
    {error && <p role="alert" className="text-sm text-rose-300">{error}</p>}
    {notice && <p role="status" className="text-sm text-emerald-300">{notice}</p>}
    <form onSubmit={save} className="grid gap-3 md:grid-cols-2">
      <label className="text-sm">Memory title<input required minLength={3} maxLength={120} value={title}
        onChange={(event) => setTitle(event.target.value)} className="mt-1 block w-full rounded border border-white/15 bg-slate-950 p-2" /></label>
      <label className="text-sm">Provenance<input required minLength={3} maxLength={240} value={provenance}
        placeholder="Operator observation or reviewed source reference" onChange={(event) => setProvenance(event.target.value)}
        className="mt-1 block w-full rounded border border-white/15 bg-slate-950 p-2" /></label>
      <label className="text-sm md:col-span-2">Memory note<textarea required minLength={10} maxLength={2_000} rows={3}
        value={content} onChange={(event) => setContent(event.target.value)} className="mt-1 block w-full rounded border border-white/15 bg-slate-950 p-2" /></label>
      <label className="text-sm">Retention<select value={days} onChange={(event) => setDays(Number(event.target.value))}
        className="mt-1 block w-full rounded border border-white/15 bg-slate-950 p-2">
        <option value={1}>1 day</option><option value={7}>7 days</option><option value={30}>30 days</option>
      </select></label>
      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={attested}
        onChange={(event) => setAttested(event.target.checked)} />I reviewed this note: no secrets or approvals</label>
      <Button disabled={busy || !snapshot || !attested || snapshot.items.length >= 50} type="submit">Save operator memory</Button>
    </form>
    {snapshot && <>
      <p className="text-xs text-slate-400">{snapshot.items.length}/{snapshot.capacity} active · {snapshot.expired_count} expired pending removal</p>
      <Button variant="secondary" disabled={busy || snapshot.expired_count === 0} onClick={() => void remove(true)}>Remove expired memory</Button>
      {snapshot.items.length === 0 && <p>No active memory notes.</p>}
      <ul className="space-y-3" aria-label="Active memory notes">
        {snapshot.items.map((item) => <li key={item.id} className="space-y-2 rounded border border-white/10 p-3">
          <h3 className="font-semibold">{item.title}</h3>
          {/* Plain escaped text only: do not render Markdown/HTML, execute instructions or link arbitrary URLs. */}
          <p className="whitespace-pre-wrap break-words text-sm text-slate-300">{item.content}</p>
          <p className="break-words text-xs text-slate-400">Provenance: {item.provenance} · by {item.created_by}</p>
          <p className="text-xs text-slate-400">Created {item.created_at} · expires {item.expires_at}</p>
          {deleteId === item.id ? <div className="flex gap-2">
            <Button disabled={busy} onClick={() => void remove(false)}>Confirm permanent deletion of {item.title}</Button>
            <Button variant="ghost" disabled={busy} onClick={() => setDeleteId("")}>Cancel deletion</Button>
          </div> : <Button variant="ghost" disabled={busy} onClick={() => setDeleteId(item.id)}>Delete memory {item.title}</Button>}
        </li>)}
      </ul>
    </>}
  </Card>;
}
