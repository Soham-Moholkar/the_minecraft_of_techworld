"use client";

import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { repositoryMCPCatalogSchema, type RepositoryMCPCatalog } from "@/lib/repository-mcp";

/** Inspect a local source-owned snapshot, not a connection to an arbitrary MCP server. */
export function RepositoryMCPExplorer() {
  const [catalog, setCatalog] = useState<RepositoryMCPCatalog | null>(null);
  const [selectedName, setSelectedName] = useState("");
  const [filter, setFilter] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    async function load() {
      try {
        const response = await fetch("/api/ai/repository/mcp/catalog", {
          cache: "no-store", signal: controller.signal,
        });
        if (!response.ok) throw new Error("unavailable catalog");
        const snapshot = repositoryMCPCatalogSchema.parse(await response.json());
        if (active) setCatalog(snapshot);
      } catch {
        if (active) setError("Local MCP catalog is unavailable. Check the local API and owner access.");
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    // An unmounted or superseded request must never replace a newer snapshot.
    return () => { active = false; controller.abort(); };
  }, [revision]);

  const tools = catalog?.tools.filter((tool) =>
    `${tool.name} ${tool.title}`.toLowerCase().includes(filter.toLowerCase())) ?? [];
  const selected = tools.find((tool) => tool.name === selectedName) ?? tools[0];

  function refresh() {
    // Clear stale permissions before requesting updated flag information.
    setCatalog(null);
    setError("");
    setLoading(true);
    setRevision((value) => value + 1);
  }

  return <Card className="mt-6 space-y-4 p-5" aria-label="MCP contract explorer">
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 className="text-lg font-semibold">Local MCP contract explorer</h2>
        <p className="text-sm text-slate-400">Source-owned contracts and permissions · no remote connections</p>
      </div>
      <Badge>Invocation disabled</Badge>
      <Button variant="secondary" disabled={loading} onClick={refresh}>Refresh contracts</Button>
    </div>
    <p className="text-sm text-slate-300">
      Inspection only. Schemas describe input shape, not authorization. Existing tenant,
      state, digest, human approval and sandbox checks still apply outside this explorer.
    </p>
    {loading && <p role="status">Loading tool contracts…</p>}
    {error && <p role="alert" className="text-sm text-rose-300">{error}</p>}
    {catalog && <>
      <p className="text-xs text-slate-400">Catalog v{catalog.catalog_version} · MCP schema revision {catalog.specification_revision} · catalog-only, not an MCP server</p>
      <label className="block text-sm">Filter tool contracts
        <input value={filter} onChange={(event) => setFilter(event.target.value)}
          className="mt-1 block w-full rounded border border-white/15 bg-slate-950 p-2" />
      </label>
      {tools.length === 0 ? <p role="status">No tool contracts match.</p> : <div className="grid gap-4 lg:grid-cols-[20rem_1fr]">
        <label className="block text-sm">Tool contract
          <select value={selected?.name ?? ""} onChange={(event) => setSelectedName(event.target.value)}
            className="mt-1 block w-full rounded border border-white/15 bg-slate-950 p-2">
            {tools.map((tool) => <option key={tool.name} value={tool.name}>{tool.title}</option>)}
          </select>
        </label>
        {selected && <div className="min-w-0 space-y-3" aria-label="Selected tool contract">
          <h3 className="font-semibold">{selected.name}</h3>
          <p className="text-sm text-slate-300">{selected.description}</p>
          <dl className="space-y-2 text-sm">
            <dt className="text-slate-400">Scope and role</dt><dd>{selected.policy.scope} · {selected.policy.required_role}</dd>
            <dt className="text-slate-400">Approval requirement</dt><dd>{selected.policy.approval}</dd>
            <dt className="text-slate-400">Execution boundary</dt><dd>{selected.policy.boundary}</dd>
            <dt className="text-slate-400">Existing REST contract (not callable here)</dt>
            <dd className="break-all font-mono text-xs">{selected.policy.rest_method} {selected.policy.rest_path}</dd>
            <dt className="text-slate-400">Source</dt><dd className="break-all font-mono text-xs">{selected.policy.source}</dd>
            <dt className="text-slate-400">Local flag eligibility</dt>
            <dd>{selected.policy.local_flags_enabled ? "Required flags enabled" : "Required flags disabled"} · not approval or worker health</dd>
            <dt className="text-slate-400">Required flags</dt>
            <dd>{selected.policy.required_flags.join(" + ") || "None for read-only inspection"}</dd>
          </dl>
          {/* React escapes schema text. No evaluator, generated form, submit action or tool call exists. */}
          <h4 className="text-sm font-semibold">Input JSON Schema</h4>
          <pre aria-label="Tool input schema" className="max-h-96 overflow-auto rounded border border-white/10 bg-slate-950 p-3 text-xs text-slate-300">
            {JSON.stringify(selected.inputSchema, null, 2)}
          </pre>
        </div>}
      </div>}
    </>}
  </Card>;
}
