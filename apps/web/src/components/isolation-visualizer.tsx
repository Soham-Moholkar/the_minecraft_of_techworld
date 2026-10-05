"use client";

import { useEffect, useReducer, useState } from "react";
import Link from "next/link";
import { CircleAlert, DatabaseZap, RefreshCw, ShieldCheck } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  type ConcurrencyProfile,
  concurrencyProfileSchema,
} from "@/lib/concurrency-profile";

const errorSchema = z.object({ detail: z.string().min(1) });

type ViewState =
  | { phase: "loading"; profile: ConcurrencyProfile | null }
  | { phase: "ready"; profile: ConcurrencyProfile }
  | { phase: "error"; profile: ConcurrencyProfile | null; message: string };

function formatIsolation(value: string | null) {
  return value === null ? "No equivalent" : value.replaceAll("_", " ");
}

function LoadingProfile() {
  return (
    <div role="status" aria-label="Loading concurrency profile" aria-live="polite" className="space-y-3 p-5">
      <span className="sr-only">Loading concurrency profile</span>
      <div className="grid gap-3 sm:grid-cols-3">
        {["engine", "isolation", "provider-setting"].map((item) => (
          <div key={item} className="h-20 animate-pulse rounded-lg border border-white/[.06] bg-white/[.025]" />
        ))}
      </div>
      <div className="h-40 animate-pulse rounded-lg border border-white/[.06] bg-white/[.025]" />
    </div>
  );
}

function EmptyProfile({ engine }: { engine: ConcurrencyProfile["engine"] }) {
  return (
    <div className="grid min-h-52 place-items-center px-6 py-10 text-center">
      <div>
        <DatabaseZap aria-hidden="true" className="mx-auto text-slate-600" size={28} />
        <h3 className="mt-4 text-sm font-semibold text-slate-200">No isolation levels reported</h3>
        <p className="mt-2 max-w-lg text-xs leading-relaxed text-slate-500">
          The {engine} provider is reachable, but it did not publish a comparison ladder. Reload the profile or inspect
          the control-plane logs before treating the database posture as verified.
        </p>
      </div>
    </div>
  );
}

const supportTone = {
  native: "success",
  mapped: "info",
  conditional: "warning",
  unsupported: "neutral",
} as const;

function IsolationMatrix({ profile }: { profile: ConcurrencyProfile }) {
  if (profile.capabilities.length === 0) return <EmptyProfile engine={profile.engine} />;

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[46rem] border-collapse text-left">
        <caption className="sr-only">
          Isolation levels supported by the active {profile.engine} database provider
        </caption>
        <thead>
          <tr className="border-b border-white/[.07] text-[9px] font-bold uppercase tracking-[.14em] text-slate-600">
            <th scope="col" className="px-5 py-3">Isolation level</th>
            <th scope="col" className="px-5 py-3">Provider support</th>
            <th scope="col" className="px-5 py-3">Effective level</th>
            <th scope="col" className="px-5 py-3">Provider behavior</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/[.06] text-[10px] leading-relaxed">
          {profile.capabilities.map((capability) => {
            const isCurrent = capability.level === profile.current_isolation;
            const isDefault = capability.level === profile.default_isolation;
            return (
              <tr key={capability.level} className={isCurrent ? "bg-cyan-300/[.035]" : undefined}>
                <th scope="row" className="px-5 py-4 align-top">
                  <div className="font-mono text-xs font-semibold text-slate-200">{formatIsolation(capability.level)}</div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {isCurrent ? <Badge tone="success">Current</Badge> : null}
                    {isDefault ? <Badge tone="info">Default</Badge> : null}
                  </div>
                </th>
                <td className="px-5 py-4 align-top">
                  <Badge tone={supportTone[capability.support]}>{capability.support}</Badge>
                </td>
                <td className="px-5 py-4 align-top font-mono text-slate-300">
                  {formatIsolation(capability.effective_level)}
                </td>
                <td className="max-w-xl px-5 py-4 align-top text-slate-500">
                  {capability.detail}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function IsolationVisualizer() {
  const [reloadVersion, reload] = useReducer((version: number) => version + 1, 0);
  const [view, setView] = useState<ViewState>({ phase: "loading", profile: null });

  useEffect(() => {
    const controller = new AbortController();
    setView((current) => ({ phase: "loading", profile: current.profile }));

    void (async () => {
      try {
        const response = await fetch("/api/database/concurrency-profile", {
          cache: "no-store",
          signal: controller.signal,
        });
        const payload: unknown = await response.json();
        if (!response.ok) {
          const parsedError = errorSchema.safeParse(payload);
          throw new Error(parsedError.success ? parsedError.data.detail : "Concurrency profile request failed");
        }
        setView({ phase: "ready", profile: concurrencyProfileSchema.parse(payload) });
      } catch (error) {
        // A superseded reload is normal. Ignoring its rejection prevents the old
        // request from overwriting fresher evidence with a false failure state.
        if (controller.signal.aborted) return;
        setView((current) => ({
          phase: "error",
          profile: current.profile,
          message: error instanceof Error ? error.message : "Concurrency profile request failed",
        }));
      }
    })();

    return () => controller.abort();
  }, [reloadVersion]);

  const profile = view.profile;

  return (
    <section aria-labelledby="isolation-title">
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-4 border-b border-white/[.07] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-violet-300">
              <ShieldCheck aria-hidden="true" size={13} />Transaction semantics
            </div>
            <h2 id="isolation-title" className="mt-2 text-lg font-semibold">Isolation and concurrency profile</h2>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-slate-500">
              Live provider defaults paired with a normalized isolation-support matrix. Support describes engine
              capability, while effective level exposes mappings and conditional behavior instead of hiding provider differences.
            </p>
          </div>
          <Button type="button" variant="secondary" onClick={reload} disabled={view.phase === "loading"}>
            <RefreshCw aria-hidden="true" size={13} />Reload profile
          </Button>
        </div>

        {view.phase === "loading" && !profile ? <LoadingProfile /> : null}
        {view.phase === "loading" && profile ? (
          <div role="status" aria-live="polite" className="border-b border-violet-300/10 bg-violet-300/[.05] px-5 py-2 text-[10px] text-violet-200">
            Refreshing concurrency evidence…
          </div>
        ) : null}
        {view.phase === "error" ? (
          <div role="alert" className="m-5 flex flex-col gap-3 rounded-lg border border-rose-400/20 bg-rose-400/[.07] p-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex gap-3">
              <CircleAlert aria-hidden="true" className="mt-0.5 shrink-0 text-rose-300" size={16} />
              <div>
                <h3 className="text-xs font-semibold text-rose-200">Concurrency profile unavailable</h3>
                <p className="mt-1 text-[10px] text-rose-200/70">{view.message}</p>
              </div>
            </div>
            <Button type="button" variant="secondary" onClick={reload}>Try again</Button>
          </div>
        ) : null}

        {profile ? (
          <>
            <dl className="grid gap-px border-b border-white/[.07] bg-white/[.07] sm:grid-cols-3">
              <div className="bg-slate-950/80 px-5 py-3">
                <dt className="text-[9px] uppercase tracking-[.14em] text-slate-600">Active engine</dt>
                <dd className="mt-1"><Badge tone="success">{profile.engine}</Badge></dd>
              </div>
              <div className="bg-slate-950/80 px-5 py-3">
                <dt className="text-[9px] uppercase tracking-[.14em] text-slate-600">Current isolation</dt>
                <dd className="mt-1 font-mono text-[10px] text-slate-300">{formatIsolation(profile.current_isolation)}</dd>
              </div>
              <div className="bg-slate-950/80 px-5 py-3">
                <dt className="text-[9px] uppercase tracking-[.14em] text-slate-600">Provider default</dt>
                <dd className="mt-1 font-mono text-[10px] text-slate-300">{formatIsolation(profile.default_isolation)}</dd>
              </div>
            </dl>
            <IsolationMatrix profile={profile} />
            {profile.notes.length > 0 ? (
              <div className="border-t border-white/[.07] px-5 py-4">
                <h3 className="text-[9px] font-bold uppercase tracking-[.14em] text-slate-600">Provider notes</h3>
                <ul className="mt-3 space-y-2 text-[10px] leading-relaxed text-slate-500">
                  {profile.notes.map((note) => (
                    <li key={note} className="border-l border-violet-300/25 pl-3">{note}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            <div className="flex flex-col gap-2 border-t border-white/[.07] px-5 py-3 text-[10px] leading-relaxed text-slate-500 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p>Isolation reduces classes of anomalies; application invariants may still require locks, constraints, or retries.</p>
                <Link href="/labs/database-isolation-locks" className="mt-2 inline-flex font-semibold text-cyan-300 hover:text-cyan-200">
                  Open the two-connection isolation lab →
                </Link>
              </div>
              <time dateTime={profile.generated_at} className="shrink-0 font-mono text-slate-600">Captured {new Date(profile.generated_at).toLocaleString()}</time>
            </div>
          </>
        ) : null}
      </Card>
    </section>
  );
}
