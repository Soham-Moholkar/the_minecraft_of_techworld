"use client";

import { useEffect, useReducer, useState } from "react";
import Link from "next/link";
import { CircleAlert, Database, RefreshCw, ShieldCheck } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  type DatabaseProviderComparison,
  databaseProviderComparisonSchema,
} from "@/lib/database-providers";

const errorSchema = z.object({ detail: z.string().min(1) });
type ViewState =
  | { phase: "loading"; comparison: DatabaseProviderComparison | null }
  | { phase: "ready"; comparison: DatabaseProviderComparison }
  | { phase: "error"; comparison: DatabaseProviderComparison | null; message: string };

function displayIsolation(value: string | null) {
  return value?.replaceAll("_", " ") ?? "Not observed";
}

export function DatabaseProviderComparisonViewer() {
  const [reloadVersion, reload] = useReducer((value: number) => value + 1, 0);
  const [view, setView] = useState<ViewState>({ phase: "loading", comparison: null });

  useEffect(() => {
    const controller = new AbortController();
    setView((current) => ({ phase: "loading", comparison: current.comparison }));
    void (async () => {
      try {
        const response = await fetch("/api/database/providers", {
          cache: "no-store",
          signal: controller.signal,
        });
        const payload: unknown = await response.json();
        if (!response.ok) {
          const error = errorSchema.safeParse(payload);
          throw new Error(error.success ? error.data.detail : "Provider comparison failed");
        }
        setView({ phase: "ready", comparison: databaseProviderComparisonSchema.parse(payload) });
      } catch (error) {
        if (controller.signal.aborted) return;
        setView((current) => ({
          phase: "error",
          comparison: current.comparison,
          message: error instanceof Error ? error.message : "Provider comparison failed",
        }));
      }
    })();
    return () => controller.abort();
  }, [reloadVersion]);

  const comparison = view.comparison;
  return (
    <section aria-labelledby="provider-comparison-title">
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-4 border-b border-white/[.07] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300">
              <Database aria-hidden="true" size={13} />Provider composition
            </div>
            <h2 id="provider-comparison-title" className="mt-2 text-lg font-semibold">Relational provider comparison</h2>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-slate-500">
              Live engine, isolation, plan format, and transaction behavior through normalized read-only probes.
            </p>
          </div>
          <Button type="button" variant="secondary" onClick={reload} disabled={view.phase === "loading"}>
            <RefreshCw aria-hidden="true" size={13} />Reload providers
          </Button>
        </div>

        {view.phase === "loading" && !comparison ? (
          <div role="status" aria-label="Loading database providers" className="grid gap-3 p-5 md:grid-cols-2">
            <span className="sr-only">Loading database providers</span>
            {["primary", "comparison"].map((item) => <div key={item} className="h-48 animate-pulse rounded-lg bg-white/[.025]" />)}
          </div>
        ) : null}
        {view.phase === "error" ? (
          <div role="alert" className="m-5 flex items-start gap-3 rounded-lg border border-rose-400/20 bg-rose-400/[.07] p-4">
            <CircleAlert aria-hidden="true" className="mt-0.5 text-rose-300" size={16} />
            <div><h3 className="text-xs font-semibold text-rose-200">Provider comparison unavailable</h3><p className="mt-1 text-[10px] text-rose-200/70">{view.message}</p></div>
          </div>
        ) : null}

        {comparison ? (
          <>
            <div className="grid gap-3 p-5 md:grid-cols-2">
              {comparison.providers.map((provider) => (
                <article key={provider.engine} className="rounded-lg border border-white/[.07] bg-white/[.025] p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div><p className="text-[9px] uppercase tracking-[.14em] text-slate-600">{provider.role} provider</p><h3 className="mt-1 font-mono text-sm font-semibold text-slate-200">{provider.engine}</h3></div>
                    <Badge tone={provider.status === "available" ? "success" : "warning"}>{provider.status}</Badge>
                  </div>
                  <dl className="mt-4 grid grid-cols-2 gap-3 text-[10px]">
                    <div><dt className="text-slate-600">Server version</dt><dd className="mt-1 font-mono text-slate-300">{provider.version ?? "Not observed"}</dd></div>
                    <div><dt className="text-slate-600">Plan format</dt><dd className="mt-1 font-mono text-slate-300">{provider.query_plan_format.replaceAll("_", " ")}</dd></div>
                    <div><dt className="text-slate-600">Current isolation</dt><dd className="mt-1 capitalize text-slate-300">{displayIsolation(provider.current_isolation)}</dd></div>
                    <div><dt className="text-slate-600">Default isolation</dt><dd className="mt-1 capitalize text-slate-300">{displayIsolation(provider.default_isolation)}</dd></div>
                  </dl>
                  <p className="mt-4 border-t border-white/[.06] pt-3 text-[10px] leading-relaxed text-slate-500">{provider.transaction_model}</p>
                  <ul className="mt-2 text-[10px] leading-relaxed text-slate-500">{provider.notes.map((note) => <li key={note}>{note}</li>)}</ul>
                </article>
              ))}
            </div>
            <div className="flex flex-col gap-3 border-t border-white/[.07] px-5 py-4 text-[10px] sm:flex-row sm:items-center sm:justify-between">
              <p className="flex items-center gap-2 text-slate-500"><ShieldCheck aria-hidden="true" size={13} className="text-emerald-300" />No SQL, credentials, hosts, users, or driver errors reach the browser.</p>
              <Link href="/labs/database-mariadb-provider" className="font-semibold text-cyan-300 hover:text-cyan-200">Open the MariaDB lab →</Link>
            </div>
          </>
        ) : null}
      </Card>
    </section>
  );
}
