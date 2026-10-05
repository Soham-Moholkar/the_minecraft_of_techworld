"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { BookOpenCheck, CircleAlert, DatabaseZap, RefreshCw, UploadCloud } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  type DocumentProjectionSnapshot,
  documentProjectionPublishSchema,
  documentProjectionSnapshotSchema,
} from "@/lib/document-projection";

const errorSchema = z.object({ detail: z.string().min(1) });
type ViewState =
  | { phase: "loading"; snapshot: DocumentProjectionSnapshot | null }
  | { phase: "ready"; snapshot: DocumentProjectionSnapshot }
  | { phase: "error"; snapshot: DocumentProjectionSnapshot | null; message: string };

function errorMessage(payload: unknown, fallback: string) {
  const parsed = errorSchema.safeParse(payload);
  return parsed.success ? parsed.data.detail : fallback;
}

function formatTimestamp(value: string | null) {
  return value ? new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value)) : "Never";
}

export function DocumentProjectionViewer() {
  const [view, setView] = useState<ViewState>({ phase: "loading", snapshot: null });
  const [publishPhase, setPublishPhase] = useState<"idle" | "publishing">("idle");
  const [publishMessage, setPublishMessage] = useState<string | null>(null);

  const loadSnapshot = useCallback(async (signal?: AbortSignal) => {
    setView((current) => ({ phase: "loading", snapshot: current.snapshot }));
    try {
      const response = await fetch("/api/database/document-projection", { cache: "no-store", signal });
      const payload: unknown = await response.json();
      if (!response.ok) throw new Error(errorMessage(payload, "Document projection request failed"));
      setView({ phase: "ready", snapshot: documentProjectionSnapshotSchema.parse(payload) });
    } catch (error) {
      if (signal?.aborted) return;
      setView((current) => ({
        phase: "error",
        snapshot: current.snapshot,
        message: error instanceof Error ? error.message : "Document projection request failed",
      }));
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void loadSnapshot(controller.signal);
    return () => controller.abort();
  }, [loadSnapshot]);

  async function publishProjection() {
    setPublishPhase("publishing");
    setPublishMessage(null);
    try {
      const response = await fetch("/api/database/document-projection", { method: "POST" });
      const payload: unknown = await response.json();
      if (!response.ok) throw new Error(errorMessage(payload, "Projection publish failed"));
      const result = documentProjectionPublishSchema.parse(payload);
      setPublishMessage(`Published ${result.published_count} documents; removed ${result.removed_count} from older generations.`);
      await loadSnapshot();
    } catch (error) {
      setPublishMessage(error instanceof Error ? error.message : "Projection publish failed");
    } finally {
      setPublishPhase("idle");
    }
  }

  const snapshot = view.snapshot;
  const unavailable = snapshot?.status === "unavailable";

  return (
    <section aria-labelledby="document-projection-title">
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-4 border-b border-white/[.07] px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-[.18em] text-cyan-300">
              <DatabaseZap aria-hidden="true" size={13} />Document read model
            </div>
            <h2 id="document-projection-title" className="mt-2 text-lg font-semibold">MongoDB project projection</h2>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-slate-500">
              Publish the authenticated tenant&apos;s relational projects into a bounded, query-ready document generation.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button type="button" variant="secondary" onClick={() => void loadSnapshot()} disabled={view.phase === "loading" || publishPhase === "publishing"}>
              <RefreshCw aria-hidden="true" size={13} />Reload
            </Button>
            <Button type="button" onClick={() => void publishProjection()} disabled={view.phase === "loading" || publishPhase === "publishing" || unavailable}>
              <UploadCloud aria-hidden="true" size={13} />{publishPhase === "publishing" ? "Publishing…" : "Publish projection"}
            </Button>
          </div>
        </div>

        {view.phase === "loading" && !snapshot ? (
          <div role="status" aria-label="Loading MongoDB projection" className="p-5">
            <div className="h-28 animate-pulse rounded-lg bg-white/[.025]" />
          </div>
        ) : null}

        {view.phase === "error" ? (
          <div role="alert" className="m-5 flex items-start gap-3 rounded-lg border border-rose-400/20 bg-rose-400/[.07] p-4">
            <CircleAlert aria-hidden="true" className="mt-0.5 text-rose-300" size={16} />
            <div><h3 className="text-xs font-semibold text-rose-200">Projection request failed</h3><p className="mt-1 text-[10px] text-rose-200/70">{view.message}</p></div>
          </div>
        ) : null}

        {snapshot ? (
          <>
            <div className="grid gap-3 p-5 md:grid-cols-3">
              <div className="rounded-lg border border-white/[.07] bg-white/[.025] p-4"><p className="text-[9px] uppercase tracking-[.14em] text-slate-600">Provider</p><div className="mt-2 flex items-center justify-between gap-2"><span className="font-mono text-sm text-slate-200">mongodb</span><Badge tone={snapshot.status === "available" ? "success" : "warning"}>{snapshot.status}</Badge></div></div>
              <div className="rounded-lg border border-white/[.07] bg-white/[.025] p-4"><p className="text-[9px] uppercase tracking-[.14em] text-slate-600">Documents</p><p className="mt-2 font-mono text-lg text-slate-200">{snapshot.document_count}</p></div>
              <div className="rounded-lg border border-white/[.07] bg-white/[.025] p-4"><p className="text-[9px] uppercase tracking-[.14em] text-slate-600">Last published</p><p className="mt-2 text-xs text-slate-300">{formatTimestamp(snapshot.published_at)}</p></div>
            </div>

            {snapshot.status === "unavailable" ? (
              <div className="mx-5 mb-5 rounded-lg border border-amber-400/20 bg-amber-400/[.06] p-4 text-xs leading-relaxed text-amber-100/75">
                Start the optional MongoDB Compose profile to publish this projection. The PostgreSQL product path remains available.
              </div>
            ) : null}
            {snapshot.status === "empty" ? (
              <div className="mx-5 mb-5 rounded-lg border border-white/[.07] bg-white/[.025] p-4 text-xs text-slate-400">
                No generation has been published for this tenant yet. Use <strong className="text-slate-200">Publish projection</strong> to create one.
              </div>
            ) : null}
            {snapshot.items.length > 0 ? (
              <div className="mx-5 mb-5 overflow-x-auto rounded-lg border border-white/[.07]">
                <table className="min-w-full text-left text-xs">
                  <caption className="sr-only">Published MongoDB project documents</caption>
                  <thead className="bg-white/[.03] text-[9px] uppercase tracking-[.14em] text-slate-500"><tr><th className="px-4 py-3" scope="col">Project</th><th className="px-4 py-3" scope="col">Status</th><th className="px-4 py-3" scope="col">Notes</th><th className="px-4 py-3" scope="col">Created</th></tr></thead>
                  <tbody>{snapshot.items.map((item) => <tr key={item.project_slug} className="border-t border-white/[.06]"><th className="px-4 py-3 font-mono font-medium text-cyan-200" scope="row">{item.project_slug}</th><td className="px-4 py-3 capitalize text-slate-300">{item.status}</td><td className="px-4 py-3 font-mono text-slate-300">{item.note_count}</td><td className="px-4 py-3 text-slate-400">{formatTimestamp(item.created_at)}</td></tr>)}</tbody>
                </table>
              </div>
            ) : null}

            <div className="grid gap-3 border-t border-white/[.07] px-5 py-4 text-[10px] md:grid-cols-2">
              <div><p className="font-semibold text-slate-300">Index strategy</p><p className="mt-1 leading-relaxed text-slate-500">{snapshot.index_strategy}</p></div>
              <div><p className="font-semibold text-slate-300">Consistency model</p><p className="mt-1 leading-relaxed text-slate-500">{snapshot.consistency_model}</p></div>
            </div>
            <div className="flex flex-col gap-3 border-t border-white/[.07] px-5 py-4 text-[10px] sm:flex-row sm:items-center sm:justify-between">
              <p className="flex max-w-2xl items-start gap-2 text-slate-500"><BookOpenCheck aria-hidden="true" size={13} className="mt-0.5 shrink-0 text-emerald-300" />Descriptions, note bodies, actors, tenant identifiers, credentials, and raw driver errors stay out of this browser contract.</p>
              <Link href="/labs/database-mongodb-document-model" className="shrink-0 font-semibold text-cyan-300 hover:text-cyan-200">Open the MongoDB lab →</Link>
            </div>
          </>
        ) : null}

        {publishMessage ? <p role="status" className="border-t border-white/[.07] px-5 py-3 text-[10px] text-slate-300">{publishMessage}</p> : null}
      </Card>
    </section>
  );
}
