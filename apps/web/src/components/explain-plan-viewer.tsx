"use client";

import { useEffect, useReducer, useState } from "react";
import Link from "next/link";
import { CircleAlert, Database, GitBranch, Lightbulb, RefreshCw } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  PROJECT_STATUS_OPTIONS,
  type QueryPlan,
  queryPlanSchema,
} from "@/lib/query-plan";

const errorSchema = z.object({ detail: z.string().min(1) });

type ViewState =
  | { phase: "loading"; plan: QueryPlan | null }
  | { phase: "ready"; plan: QueryPlan }
  | { phase: "error"; plan: QueryPlan | null; message: string };

function formatEstimate(value: number | null) {
  return value === null ? "Not reported" : new Intl.NumberFormat("en", { maximumFractionDigits: 2 }).format(value);
}

function LoadingPlan() {
  return (
    <div role="status" aria-label="Loading query plan" aria-live="polite" className="space-y-3 p-5">
      <span className="sr-only">Loading query plan</span>
      {["w-2/5", "w-4/5", "w-3/5"].map((width) => (
        <div key={width} className="rounded-lg border border-white/[.06] bg-white/[.025] p-4">
          <div className={`h-3 rounded bg-white/[.08] ${width}`} />
          <div className="mt-3 h-2 w-full rounded bg-white/[.05]" />
        </div>
      ))}
    </div>
  );
}

function EmptyPlan({ status }: { status: string }) {
  return (
    <div className="grid min-h-56 place-items-center px-6 py-10 text-center">
      <div>
        <GitBranch aria-hidden="true" className="mx-auto text-slate-600" size={28} />
        <h3 className="mt-4 text-sm font-semibold text-slate-200">No plan nodes returned</h3>
        <p className="mt-2 max-w-md text-xs leading-relaxed text-slate-500">
          The database accepted the <span className="font-mono text-slate-300">{status}</span> filter but did not
          expose a normalized operation. Reload the plan or inspect the API logs.
        </p>
      </div>
    </div>
  );
}

function PlanNodes({ plan }: { plan: QueryPlan }) {
  if (plan.nodes.length === 0) return <EmptyPlan status={plan.parameters.status} />;

  return (
    <ol aria-label="Normalized query plan operations" className="space-y-3 p-5">
      {plan.nodes.map((node, index) => (
        <li key={`${node.operation}-${node.relation ?? "none"}-${index}`} className="relative pl-9">
          {index < plan.nodes.length - 1 ? (
            <span aria-hidden="true" className="absolute left-[13px] top-7 h-[calc(100%+12px)] w-px bg-cyan-300/20" />
          ) : null}
          <span className="absolute left-0 top-3 grid size-7 place-items-center rounded-full border border-cyan-300/20 bg-cyan-300/[.08] font-mono text-[10px] font-bold text-cyan-300">
            {index + 1}
          </span>
          <div className="rounded-lg border border-white/[.07] bg-white/[.025] p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <code className="text-xs font-semibold text-slate-100">{node.operation}</code>
                {node.relation ? <Badge tone="info">{node.relation}</Badge> : null}
              </div>
              <dl className="flex gap-4 text-right text-[10px]">
                <div>
                  <dt className="text-slate-600">Estimated rows</dt>
                  <dd className="mt-1 font-mono text-slate-300">{formatEstimate(node.estimated_rows)}</dd>
                </div>
                <div>
                  <dt className="text-slate-600">Estimated cost</dt>
                  <dd className="mt-1 font-mono text-slate-300">{formatEstimate(node.estimated_cost)}</dd>
                </div>
              </dl>
            </div>
            <p className="mt-3 break-words font-mono text-[10px] leading-relaxed text-slate-500">{node.detail}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}

export function ExplainPlanViewer() {
  const [status, setStatus] = useState<(typeof PROJECT_STATUS_OPTIONS)[number]>("active");
  const [reloadVersion, reload] = useReducer((version: number) => version + 1, 0);
  const [view, setView] = useState<ViewState>({ phase: "loading", plan: null });

  useEffect(() => {
    const controller = new AbortController();
    setView((current) => ({ phase: "loading", plan: current.plan }));

    void (async () => {
      try {
        const response = await fetch(`/api/database/query-plan?status=${encodeURIComponent(status)}`, {
          cache: "no-store",
          signal: controller.signal,
        });
        const payload: unknown = await response.json();
        if (!response.ok) {
          const error = errorSchema.safeParse(payload);
          throw new Error(error.success ? error.data.detail : "Query plan request failed");
        }
        const plan = queryPlanSchema.parse(payload);
        setView({ phase: "ready", plan });
      } catch (error) {
        // Aborted requests are expected when an operator changes the filter
        // quickly. Suppressing them prevents stale request noise and state.
        if (controller.signal.aborted) return;
        setView((current) => ({
          phase: "error",
          plan: current.plan,
          message: error instanceof Error ? error.message : "Query plan request failed",
        }));
      }
    })();

    return () => controller.abort();
  }, [reloadVersion, status]);

  const plan = view.plan;
  return (
    <section aria-labelledby="query-plan-title" className="grid gap-6 xl:grid-cols-[minmax(0,1.65fr)_minmax(18rem,.75fr)]">
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-4 border-b border-white/[.07] px-5 py-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300">
              <Database aria-hidden="true" size={13} />Live database evidence
            </div>
            <h2 id="query-plan-title" className="mt-2 text-lg font-semibold">Explain plan viewer</h2>
            <p className="mt-1 text-xs text-slate-500">Tenant-scoped, read-only, and normalized across PostgreSQL and SQLite.</p>
          </div>
          <div className="flex flex-wrap items-end gap-2">
            <label className="grid gap-1 text-[10px] font-semibold uppercase tracking-[.12em] text-slate-500">
              Project status
              <select
                value={status}
                onChange={(event) => setStatus(event.target.value as (typeof PROJECT_STATUS_OPTIONS)[number])}
                className="h-9 rounded-lg border border-white/10 bg-slate-950 px-3 text-xs font-medium normal-case tracking-normal text-slate-100 outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
              >
                {PROJECT_STATUS_OPTIONS.map((option) => <option key={option} value={option}>{option}</option>)}
              </select>
            </label>
            <Button type="button" variant="secondary" onClick={reload} disabled={view.phase === "loading"}>
              <RefreshCw aria-hidden="true" size={13} />Reload plan
            </Button>
          </div>
        </div>

        {plan ? (
          <div className="grid gap-px border-b border-white/[.07] bg-white/[.07] sm:grid-cols-3">
            <div className="bg-slate-950/80 px-5 py-3"><div className="text-[9px] uppercase tracking-[.14em] text-slate-600">Engine</div><div className="mt-1"><Badge tone="success">{plan.engine}</Badge></div></div>
            <div className="bg-slate-950/80 px-5 py-3"><div className="text-[9px] uppercase tracking-[.14em] text-slate-600">Allowlisted query</div><div className="mt-1 truncate font-mono text-[10px] text-slate-300">{plan.query_name}</div></div>
            <div className="bg-slate-950/80 px-5 py-3"><div className="text-[9px] uppercase tracking-[.14em] text-slate-600">Generated</div><time dateTime={plan.generated_at} className="mt-1 block text-[10px] text-slate-300">{new Date(plan.generated_at).toLocaleString()}</time></div>
          </div>
        ) : null}

        {view.phase === "loading" && !plan ? <LoadingPlan /> : null}
        {view.phase === "loading" && plan ? <div role="status" className="border-b border-cyan-300/10 bg-cyan-300/[.05] px-5 py-2 text-[10px] text-cyan-200">Refreshing plan evidence…</div> : null}
        {view.phase === "error" ? (
          <div role="alert" className="m-5 flex flex-col gap-3 rounded-lg border border-rose-400/20 bg-rose-400/[.07] p-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-3"><CircleAlert aria-hidden="true" className="mt-0.5 shrink-0 text-rose-300" size={16} /><div><h3 className="text-xs font-semibold text-rose-200">Plan unavailable</h3><p className="mt-1 text-[10px] text-rose-200/70">{view.message}</p></div></div>
            <Button type="button" variant="secondary" onClick={reload}>Try again</Button>
          </div>
        ) : null}
        {plan ? <PlanNodes plan={plan} /> : null}
      </Card>

      <div className="space-y-6">
        <Card className="p-5">
          <div className="flex items-center gap-2"><GitBranch aria-hidden="true" size={14} className="text-cyan-300" /><h2 className="text-sm font-semibold">How to read this</h2></div>
          <ol className="mt-4 space-y-3 text-[10px] leading-relaxed text-slate-500">
            <li><span className="font-semibold text-slate-300">1. Follow operations top to bottom.</span> Each node describes how the selected provider finds or combines rows.</li>
            <li><span className="font-semibold text-slate-300">2. Check relation and estimates.</span> Large row estimates or scans are signals to investigate, not automatic failures.</li>
            <li><span className="font-semibold text-slate-300">3. Compare providers in code.</span> The normalized view keeps the product stable while engine-specific detail remains visible.</li>
          </ol>
        </Card>
        <Card className="p-5">
          <div className="flex items-center gap-2"><Lightbulb aria-hidden="true" size={14} className="text-amber-300" /><h2 className="text-sm font-semibold">Recommendations</h2></div>
          {plan?.recommendations.length ? (
            <ul className="mt-4 space-y-3 text-[10px] leading-relaxed text-slate-400">
              {plan.recommendations.map((recommendation) => <li key={recommendation} className="border-l border-amber-300/25 pl-3">{recommendation}</li>)}
            </ul>
          ) : (
            <p className="mt-4 text-[10px] leading-relaxed text-slate-500">Recommendations appear after a valid plan is loaded.</p>
          )}
          <Link href="/labs/database-query-plans" className="mt-5 inline-flex text-[10px] font-semibold text-cyan-300 hover:text-cyan-200">
            Open the resettable query-plan lab →
          </Link>
        </Card>
      </div>
    </section>
  );
}
