"use client";

import Link from "next/link";
import { useEffect, useReducer, useState } from "react";
import { CircleAlert, EyeOff, LockKeyhole, RefreshCw, TimerReset } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { type LockActivity, lockActivitySchema } from "@/lib/lock-activity";

const errorSchema = z.object({ detail: z.string().min(1) });

type ViewState =
  | { phase: "loading"; activity: LockActivity | null }
  | { phase: "ready"; activity: LockActivity }
  | { phase: "error"; activity: LockActivity | null; message: string };

function LoadingActivity() {
  return (
    <div role="status" aria-label="Loading lock activity" aria-live="polite" className="space-y-3 p-5">
      <span className="sr-only">Loading lock activity</span>
      <div className="grid gap-3 sm:grid-cols-3">
        {["provider", "locks", "waiters"].map((item) => (
          <div key={item} className="h-20 animate-pulse rounded-lg border border-white/[.06] bg-white/[.025]" />
        ))}
      </div>
      <div className="h-36 animate-pulse rounded-lg border border-white/[.06] bg-white/[.025]" />
    </div>
  );
}

function UnavailableActivity({ activity }: { activity: LockActivity }) {
  return (
    <div className="grid min-h-52 place-items-center px-6 py-10 text-center">
      <div>
        <EyeOff aria-hidden="true" className="mx-auto text-slate-600" size={28} />
        <h3 className="mt-4 text-sm font-semibold text-slate-200">Live lock catalog unavailable</h3>
        <p className="mt-2 max-w-xl text-xs leading-relaxed text-slate-500">
          {activity.engine} does not expose a reviewed, portable lock-activity catalog. This is an explicit provider
          limitation, not a claim that no locks exist.
        </p>
      </div>
    </div>
  );
}

function ActivityBuckets({ activity }: { activity: LockActivity }) {
  if (!activity.available) return <UnavailableActivity activity={activity} />;
  if (activity.buckets.length === 0) {
    return (
      <div className="grid min-h-40 place-items-center px-6 py-10 text-center">
        <div>
          <LockKeyhole aria-hidden="true" className="mx-auto text-emerald-300" size={26} />
          <h3 className="mt-3 text-sm font-semibold text-slate-200">No database-scoped locks reported</h3>
          <p className="mt-2 text-xs text-slate-500">The snapshot completed successfully and returned no aggregate buckets.</p>
        </div>
      </div>
    );
  }

  const largestBucket = Math.max(...activity.buckets.map((bucket) => bucket.count), 1);
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[34rem] border-collapse text-left">
        <caption className="sr-only">Aggregate lock modes for the active {activity.engine} database</caption>
        <thead>
          <tr className="border-b border-white/[.07] text-[9px] font-bold uppercase tracking-[.14em] text-slate-600">
            <th scope="col" className="px-5 py-3">Lock mode</th>
            <th scope="col" className="px-5 py-3">State</th>
            <th scope="col" className="px-5 py-3">Count</th>
            <th scope="col" className="px-5 py-3">Relative activity</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[.06] text-[10px]">
          {activity.buckets.map((bucket) => (
            <tr key={`${bucket.mode}-${bucket.granted ? "granted" : "waiting"}`}>
              <th scope="row" className="px-5 py-4 font-mono text-xs font-semibold text-slate-200">{bucket.mode}</th>
              <td className="px-5 py-4">
                <Badge tone={bucket.granted ? "success" : "warning"}>{bucket.granted ? "Granted" : "Waiting"}</Badge>
              </td>
              <td className="px-5 py-4 font-mono text-slate-300">{bucket.count}</td>
              <td className="w-2/5 px-5 py-4">
                <div aria-hidden="true" className="h-1.5 overflow-hidden rounded-full bg-white/[.06]">
                  <div
                    className={`h-full rounded-full ${bucket.granted ? "bg-emerald-300/70" : "bg-amber-300/80"}`}
                    style={{ width: `${Math.max((bucket.count / largestBucket) * 100, 4)}%` }}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function LockActivityViewer() {
  const [reloadVersion, reload] = useReducer((version: number) => version + 1, 0);
  const [view, setView] = useState<ViewState>({ phase: "loading", activity: null });

  useEffect(() => {
    const controller = new AbortController();
    setView((current) => ({ phase: "loading", activity: current.activity }));

    void (async () => {
      try {
        const response = await fetch("/api/database/lock-activity", {
          cache: "no-store",
          signal: controller.signal,
        });
        const payload: unknown = await response.json();
        if (!response.ok) {
          const parsedError = errorSchema.safeParse(payload);
          throw new Error(parsedError.success ? parsedError.data.detail : "Lock activity request failed");
        }
        setView({ phase: "ready", activity: lockActivitySchema.parse(payload) });
      } catch (error) {
        // Reload aborts are expected. The old request must not overwrite newer
        // evidence with a stale error after its replacement has started.
        if (controller.signal.aborted) return;
        setView((current) => ({
          phase: "error",
          activity: current.activity,
          message: error instanceof Error ? error.message : "Lock activity request failed",
        }));
      }
    })();

    return () => controller.abort();
  }, [reloadVersion]);

  const activity = view.activity;
  return (
    <section aria-labelledby="lock-activity-title">
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-4 border-b border-white/[.07] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-amber-300">
              <TimerReset aria-hidden="true" size={13} />Instantaneous evidence
            </div>
            <h2 id="lock-activity-title" className="mt-2 text-lg font-semibold">Live lock activity</h2>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-slate-500">
              Database-wide lock modes grouped into granted and waiting counts. This is a point-in-time signal for
              investigation, not a historical trace or proof of a performance incident.
            </p>
          </div>
          <Button type="button" variant="secondary" onClick={reload} disabled={view.phase === "loading"}>
            <RefreshCw aria-hidden="true" size={13} />Reload snapshot
          </Button>
        </div>

        {view.phase === "loading" && !activity ? <LoadingActivity /> : null}
        {view.phase === "loading" && activity ? (
          <div role="status" aria-live="polite" className="border-b border-amber-300/10 bg-amber-300/[.05] px-5 py-2 text-[10px] text-amber-200">
            Refreshing lock evidence…
          </div>
        ) : null}
        {view.phase === "error" ? (
          <div role="alert" className="m-5 flex flex-col gap-3 rounded-lg border border-rose-400/20 bg-rose-400/[.07] p-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-3">
              <CircleAlert aria-hidden="true" className="mt-0.5 shrink-0 text-rose-300" size={16} />
              <div>
                <h3 className="text-xs font-semibold text-rose-200">Lock activity unavailable</h3>
                <p className="mt-1 text-[10px] text-rose-200/70">{view.message}</p>
              </div>
            </div>
            <Button type="button" variant="secondary" onClick={reload}>Try again</Button>
          </div>
        ) : null}

        {activity ? (
          <>
            <dl className="grid gap-px border-b border-white/[.07] bg-white/[.07] sm:grid-cols-3">
              <div className="bg-slate-950/80 px-5 py-3">
                <dt className="text-[9px] uppercase tracking-[.14em] text-slate-600">Active engine</dt>
                <dd className="mt-1"><Badge tone={activity.available ? "success" : "neutral"}>{activity.engine}</Badge></dd>
              </div>
              <div className="bg-slate-950/80 px-5 py-3">
                <dt className="text-[9px] uppercase tracking-[.14em] text-slate-600">Total locks</dt>
                <dd className="mt-1 font-mono text-sm font-semibold text-slate-200">{activity.total_locks}</dd>
              </div>
              <div className="bg-slate-950/80 px-5 py-3">
                <dt className="text-[9px] uppercase tracking-[.14em] text-slate-600">Waiting locks</dt>
                <dd className={`mt-1 font-mono text-sm font-semibold ${activity.waiting_locks > 0 ? "text-amber-300" : "text-emerald-300"}`}>
                  {activity.waiting_locks}
                </dd>
              </div>
            </dl>
            <ActivityBuckets activity={activity} />
            <div className="grid gap-4 border-t border-white/[.07] px-5 py-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
              <div>
                <div className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[.14em] text-slate-600">
                  <EyeOff aria-hidden="true" size={12} />Privacy boundary
                </div>
                <p className="mt-2 text-[10px] leading-relaxed text-slate-500">
                  Relation names, query text, process IDs, transaction IDs, and tenant rows are intentionally omitted.
                </p>
                {activity.notes.length > 0 ? (
                  <ul className="mt-3 space-y-2 text-[10px] leading-relaxed text-slate-500">
                    {activity.notes.map((note) => <li key={note} className="border-l border-amber-300/25 pl-3">{note}</li>)}
                  </ul>
                ) : null}
              </div>
              <div className="text-left md:text-right">
                <Link href="/labs/database-postgresql-concurrency" className="inline-flex text-[10px] font-semibold text-cyan-300 hover:text-cyan-200">
                  Open the PostgreSQL concurrency lab →
                </Link>
                <time dateTime={activity.generated_at} className="mt-2 block font-mono text-[10px] text-slate-600">
                  Captured {new Date(activity.generated_at).toLocaleString()}
                </time>
              </div>
            </div>
          </>
        ) : null}
      </Card>
    </section>
  );
}
