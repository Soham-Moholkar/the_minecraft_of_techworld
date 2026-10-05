"use client";

import Link from "next/link";
import { useEffect, useReducer, useState, type FormEvent } from "react";
import { CircleAlert, Database, Gauge, RefreshCw, Search, ShieldCheck } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  PROJECT_STATUS_OPTIONS,
  databaseCacheProfileSchema,
  databaseWorkbenchSchema,
  type DatabaseCacheProfile,
  type DatabaseWorkbench,
} from "@/lib/phase-four";

const errorSchema = z.object({ detail: z.string().min(1) });
type CacheState =
  | { phase: "loading"; profile: DatabaseCacheProfile | null }
  | { phase: "ready"; profile: DatabaseCacheProfile }
  | { phase: "error"; profile: DatabaseCacheProfile | null; message: string };

export function DatabaseOperationsWorkbench() {
  const [cacheVersion, reloadCache] = useReducer((version: number) => version + 1, 0);
  const [cache, setCache] = useState<CacheState>({ phase: "loading", profile: null });
  const [status, setStatus] = useState<(typeof PROJECT_STATUS_OPTIONS)[number]>("active");
  const [limit, setLimit] = useState(10);
  const [result, setResult] = useState<DatabaseWorkbench | null>(null);
  const [queryState, setQueryState] = useState<"idle" | "loading" | "error">("idle");
  const [queryError, setQueryError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    setCache((current) => ({ phase: "loading", profile: current.profile }));
    void (async () => {
      try {
        const response = await fetch("/api/database/cache-profile", {
          cache: "no-store",
          signal: controller.signal,
        });
        const payload: unknown = await response.json();
        if (!response.ok) {
          const parsedError = errorSchema.safeParse(payload);
          throw new Error(parsedError.success ? parsedError.data.detail : "Cache request failed");
        }
        setCache({ phase: "ready", profile: databaseCacheProfileSchema.parse(payload) });
      } catch (error) {
        if (controller.signal.aborted) return;
        setCache((current) => ({
          phase: "error",
          profile: current.profile,
          message: error instanceof Error ? error.message : "Cache request failed",
        }));
      }
    })();
    return () => controller.abort();
  }, [cacheVersion]);

  async function runQuery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setQueryState("loading");
    setQueryError("");
    try {
      const response = await fetch("/api/database/workbench", {
        method: "POST",
        cache: "no-store",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_name: "tenant_projects_by_status", status, limit }),
      });
      const payload: unknown = await response.json();
      if (!response.ok) {
        const parsedError = errorSchema.safeParse(payload);
        throw new Error(parsedError.success ? parsedError.data.detail : "Query failed");
      }
      setResult(databaseWorkbenchSchema.parse(payload));
      setQueryState("idle");
    } catch (error) {
      setQueryError(error instanceof Error ? error.message : "Query failed");
      setQueryState("error");
    }
  }

  const profile = cache.profile;
  return (
    <section aria-labelledby="operations-workbench-title" className="grid gap-6 xl:grid-cols-2">
      <Card className="overflow-hidden">
        <div className="flex items-start justify-between gap-4 border-b border-white/[.07] p-5">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-violet-300">
              <Gauge aria-hidden="true" size={13} />Cache-aside evidence
            </div>
            <h2 id="operations-workbench-title" className="mt-2 text-lg font-semibold">Redis portfolio cache</h2>
            <p className="mt-1 text-xs text-slate-500">SQL stays authoritative when the optional cache is absent.</p>
          </div>
          <Button type="button" variant="secondary" onClick={reloadCache} disabled={cache.phase === "loading"}>
            <RefreshCw aria-hidden="true" size={13} />Refresh
          </Button>
        </div>
        {cache.phase === "loading" && !profile ? <p role="status" className="p-5 text-xs text-slate-400">Loading cache evidence…</p> : null}
        {cache.phase === "error" ? <p role="alert" className="m-5 flex gap-2 rounded-lg border border-rose-400/20 bg-rose-400/[.07] p-3 text-xs text-rose-200"><CircleAlert aria-hidden="true" size={15} />{cache.message}</p> : null}
        {profile ? (
          <div className="space-y-5 p-5">
            <div className="flex flex-wrap gap-2">
              <Badge tone={profile.status === "available" ? "success" : "warning"}>Redis {profile.status}</Badge>
              <Badge tone={profile.cache_state === "hit" ? "success" : "info"}>{profile.cache_state}</Badge>
              <Badge>{profile.ttl_seconds}s TTL</Badge>
            </div>
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-lg border border-white/[.07] p-3"><dt className="text-[9px] uppercase tracking-wider text-slate-600">Projects</dt><dd className="mt-1 text-xl font-semibold">{profile.project_total}</dd></div>
              {profile.status_counts.map((item) => <div key={item.status} className="rounded-lg border border-white/[.07] p-3"><dt className="text-[9px] uppercase tracking-wider text-slate-600">{item.status}</dt><dd className="mt-1 text-xl font-semibold">{item.count}</dd></div>)}
            </dl>
            <p className="text-[10px] leading-relaxed text-slate-500">{profile.consistency_model}</p>
            <Link href="/labs/database-redis-cache-streams" className="text-[10px] font-semibold text-cyan-300">Open cache, Streams, WATCH, and ACL lab →</Link>
          </div>
        ) : null}
      </Card>

      <Card className="overflow-hidden">
        <form onSubmit={runQuery}>
          <div className="border-b border-white/[.07] p-5">
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300"><Database aria-hidden="true" size={13} />Safe query workbench</div>
            <h2 className="mt-2 text-lg font-semibold">Tenant projects by status</h2>
            <p className="mt-1 text-xs text-slate-500">A reviewed template with bound values—not an arbitrary SQL console.</p>
            <div className="mt-4 flex flex-wrap items-end gap-3">
              <label className="grid gap-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">Status
                <select value={status} onChange={(event) => setStatus(event.target.value as typeof status)} className="h-9 rounded-lg border border-white/10 bg-slate-950 px-3 text-xs normal-case tracking-normal text-white focus-visible:ring-2 focus-visible:ring-cyan-400">
                  {PROJECT_STATUS_OPTIONS.map((option) => <option key={option}>{option}</option>)}
                </select>
              </label>
              <label className="grid gap-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">Row limit
                <input type="number" min={1} max={25} value={limit} onChange={(event) => setLimit(Number(event.target.value))} className="h-9 w-24 rounded-lg border border-white/10 bg-slate-950 px-3 text-xs normal-case tracking-normal text-white focus-visible:ring-2 focus-visible:ring-cyan-400" />
              </label>
              <Button type="submit" disabled={queryState === "loading"}><Search aria-hidden="true" size={13} />{queryState === "loading" ? "Running…" : "Run query"}</Button>
            </div>
          </div>
        </form>
        {queryState === "error" ? <p role="alert" className="m-5 rounded-lg border border-rose-400/20 bg-rose-400/[.07] p-3 text-xs text-rose-200">{queryError}</p> : null}
        {result ? (
          <div className="p-5">
            <div className="mb-4 flex flex-wrap items-center gap-2"><Badge tone="success">{result.engine}</Badge><Badge>{result.returned_count} rows</Badge></div>
            {result.items.length === 0 ? <p className="py-8 text-center text-xs text-slate-500">No projects match this tenant-scoped filter.</p> : (
              <div className="overflow-x-auto"><table className="w-full min-w-[28rem] text-left text-xs"><caption className="sr-only">Tenant projects returned by the reviewed query</caption><thead className="text-[9px] uppercase tracking-wider text-slate-600"><tr><th className="pb-2">Project</th><th className="pb-2">Status</th><th className="pb-2">Notes</th><th className="pb-2">Created</th></tr></thead><tbody>{result.items.map((item) => <tr key={item.project_slug} className="border-t border-white/[.06]"><td className="py-3 font-mono text-cyan-200">{item.project_slug}</td><td className="py-3">{item.status}</td><td className="py-3">{item.note_count}</td><td className="py-3 text-slate-500">{new Date(item.created_at).toLocaleDateString()}</td></tr>)}</tbody></table></div>
            )}
            <p className="mt-4 flex gap-2 text-[10px] leading-relaxed text-slate-500"><ShieldCheck aria-hidden="true" className="shrink-0 text-emerald-300" size={14} />{result.safety_model}</p>
          </div>
        ) : <p className="p-5 text-xs text-slate-500">Choose bounded parameters and run the reviewed query.</p>}
        <div className="flex flex-wrap gap-4 border-t border-white/[.07] px-5 py-4 text-[10px] font-semibold text-cyan-300">
          <Link href="/labs/database-provider-benchmarks">Benchmark evidence →</Link>
          <Link href="/labs/database-security-boundaries">Security exercise →</Link>
        </div>
      </Card>
    </section>
  );
}
