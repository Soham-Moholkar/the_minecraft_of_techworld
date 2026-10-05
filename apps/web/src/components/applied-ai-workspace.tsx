"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  appliedExperimentSchema, appliedListSchema, taskLabel,
  type AppliedExperiment, type AppliedSummary,
} from "@/lib/applied-ai";

async function responseBody(response: Response): Promise<unknown> {
  const body: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body
      && typeof body.detail === "string" ? body.detail : "Applied AI request failed.";
    throw new Error(detail);
  }
  return body;
}

export function AppliedAIWorkspace() {
  const [name, setName] = useState("Phase 7 applied AI compatibility");
  const [history, setHistory] = useState<AppliedSummary[]>([]);
  const [selected, setSelected] = useState<AppliedExperiment | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const active = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/ml/applied-experiments", { cache: "no-store", signal: controller.signal })
      .then(responseBody).then((body) => setHistory(appliedListSchema.parse(body)))
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "History unavailable.");
      }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => { controller.abort(); active.current?.abort(); };
  }, []);

  async function inspect(id: string) {
    active.current?.abort();
    const controller = new AbortController(); active.current = controller;
    setError(""); setLoading(true);
    try {
      const body = await responseBody(await fetch(`/api/ml/applied-experiments?id=${id}`, {
        cache: "no-store", signal: controller.signal,
      }));
      if (!controller.signal.aborted) setSelected(appliedExperimentSchema.parse(body));
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Evidence unavailable.");
    } finally { if (!controller.signal.aborted) setLoading(false); }
  }

  async function run(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); active.current?.abort();
    const controller = new AbortController(); active.current = controller;
    setRunning(true); setError(""); setSelected(null);
    try {
      const body = await responseBody(await fetch("/api/ml/applied-experiments", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }), signal: controller.signal,
      }));
      const experiment = appliedExperimentSchema.parse(body);
      if (!controller.signal.aborted) {
        setSelected(experiment); setHistory((current) => [experiment, ...current]);
      }
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Run failed.");
    } finally { if (!controller.signal.aborted) setRunning(false); }
  }

  return <section className="space-y-6 border-t border-white/10 pt-8" aria-labelledby="applied-ai-title">
    <header><p className="text-xs uppercase tracking-widest text-violet-300">Applied AI · Phase 7</p>
      <h2 id="applied-ai-title" className="mt-2 text-2xl font-semibold">Framework compatibility suite</h2>
      <p className="mt-2 max-w-3xl text-sm text-slate-400">Run real bounded CNN, GRU, Transformer, and recommendation models over deterministic ATLAS fixtures. Results are compatibility evidence, not external benchmark claims.</p></header>
    {error ? <p role="alert" className="rounded-lg border border-rose-400/30 p-4 text-sm text-rose-200">{error}</p> : null}
    <div className="grid gap-6 xl:grid-cols-[1fr_1.3fr]">
      <Card className="p-5"><h3 className="font-semibold">Run all four tasks</h3>
        <form className="mt-4 space-y-4" onSubmit={run}><label className="block text-xs text-slate-300">Run name<input className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm focus-visible:outline-2 focus-visible:outline-violet-400" required minLength={2} maxLength={120} value={name} onChange={(event) => setName(event.target.value)} /></label>
          <Button disabled={running || loading} type="submit">{running ? "Running four models…" : "Run applied suite"}</Button>
          {running ? <p role="status" className="text-xs text-violet-200">Training on one CPU thread with a 90 second process limit…</p> : null}
        </form></Card>
      <Card className="p-5"><h3 className="font-semibold">Saved suite runs</h3>
        {loading ? <p role="status" className="mt-4 text-sm text-slate-400">Loading applied evidence…</p> : null}
        {!loading && history.length === 0 ? <p className="mt-4 text-sm text-slate-400">No applied runs yet.</p> : null}
        <ul className="mt-4 space-y-2">{history.map((item) => <li key={item.id}><button type="button" disabled={running} onClick={() => void inspect(item.id)} className="flex w-full items-center justify-between rounded-lg border border-white/10 p-3 text-left text-sm hover:bg-white/5 focus-visible:outline-2 focus-visible:outline-violet-400"><span>{item.name}</span><Badge>{item.improved_tasks}/{item.tasks} improved</Badge></button></li>)}</ul>
      </Card>
    </div>
    {selected ? <div role="region" aria-label="Applied AI report" className="space-y-4">
      <div><h3 className="text-xl font-semibold">{selected.name}</h3><p className="mt-1 text-xs text-slate-400">PyTorch {selected.report.torch_version} · seed {selected.report.random_seed}</p></div>
      <div className="grid gap-4 lg:grid-cols-2">{selected.report.tasks.map((task) => {
        const maximum = Math.max(...task.training_curve.map((point) => point.loss), 0.001);
        const width = 360; const divisor = Math.max(1, task.training_curve.length - 1);
        const points = task.training_curve.map((point, index) => `${index * width / divisor},${100 - point.loss / maximum * 90}`).join(" ");
        const format = (value: number) => task.metric === "mae" ? value.toFixed(2) : `${(value * 100).toFixed(1)}%`;
        return <Card className="min-w-0 p-5" key={task.task}><div className="flex items-start justify-between gap-3"><div><h4 className="font-semibold">{taskLabel[task.task]}</h4><p className="mt-1 text-xs text-slate-400">{task.architecture} · {task.train_examples}/{task.test_examples} train/test</p></div><Badge>{task.metric.replaceAll("_", " ")}</Badge></div>
          <dl className="mt-4 grid grid-cols-2 gap-3"><div><dt className="text-xs text-slate-500">Model</dt><dd className="text-xl">{format(task.model_score)}</dd></div><div><dt className="text-xs text-slate-500">{task.baseline}</dt><dd className="text-xl">{format(task.baseline_score)}</dd></div></dl>
          <svg viewBox="0 0 360 110" className="mt-4 h-28 w-full" role="img" aria-label={`${taskLabel[task.task]} training loss`}><polyline points={points} fill="none" stroke="currentColor" strokeWidth="2" className="text-violet-300" /></svg>
        </Card>;
      })}</div>
      <Card className="p-5"><h4 className="font-semibold">Scope and limits</h4><ul className="mt-3 space-y-2 text-xs text-slate-400">{selected.report.caveats.map((caveat) => <li key={caveat}>{caveat}</li>)}</ul></Card>
    </div> : null}
  </section>;
}
