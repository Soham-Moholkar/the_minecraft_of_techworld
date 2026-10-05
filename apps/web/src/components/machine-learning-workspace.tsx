"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { datasetListSchema, type DatasetSummary } from "@/lib/datasets";
import {
  displayModel, experimentListSchema, experimentSchema,
  type Experiment, type ExperimentSummary,
} from "@/lib/machine-learning";

async function payload(response: Response): Promise<unknown> {
  const body: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body && typeof body.detail === "string"
      ? body.detail : "Model request failed.";
    throw new Error(detail);
  }
  return body;
}

export function MachineLearningWorkspace() {
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [catalog, setCatalog] = useState<ExperimentSummary[]>([]);
  const [selected, setSelected] = useState<Experiment | null>(null);
  const [datasetId, setDatasetId] = useState("");
  const [name, setName] = useState("Service cost risk comparison");
  const [suite, setSuite] = useState<"classical" | "neural" | "frameworks">("classical");
  const [loading, setLoading] = useState(true);
  const [training, setTraining] = useState(false);
  const [error, setError] = useState("");
  const request = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      fetch("/api/datasets", { cache: "no-store", signal: controller.signal }).then(payload),
      fetch("/api/ml/experiments", { cache: "no-store", signal: controller.signal }).then(payload),
    ]).then(([datasetBody, experimentBody]) => {
      const parsedDatasets = datasetListSchema.parse(datasetBody);
      setDatasets(parsedDatasets);
      setDatasetId(parsedDatasets.find((item) => item.valid_rows >= 20)?.id ?? "");
      setCatalog(experimentListSchema.parse(experimentBody));
    }).catch((reason: unknown) => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Model workspace unavailable.");
    }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => { controller.abort(); request.current?.abort(); };
  }, []);

  async function inspect(id: string) {
    request.current?.abort();
    const controller = new AbortController();
    request.current = controller;
    setError(""); setSelected(null); setLoading(true);
    try {
      const body = await payload(await fetch(`/api/ml/experiments?id=${id}`, {
        cache: "no-store", signal: controller.signal,
      }));
      if (!controller.signal.aborted) setSelected(experimentSchema.parse(body));
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Experiment unavailable.");
    } finally { if (!controller.signal.aborted) setLoading(false); }
  }

  async function train(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    request.current?.abort();
    const controller = new AbortController();
    request.current = controller;
    setTraining(true); setError(""); setSelected(null);
    try {
      const body = await payload(await fetch("/api/ml/experiments", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, dataset_id: datasetId, suite }), signal: controller.signal,
      }));
      const experiment = experimentSchema.parse(body);
      if (!controller.signal.aborted) {
        setSelected(experiment); setCatalog((current) => [experiment, ...current]);
      }
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Training failed.");
    } finally {
      if (!controller.signal.aborted) setTraining(false);
      if (request.current === controller) request.current = null;
    }
  }

  const report = selected?.report;
  const logistic = report?.models.find((model) => model.model === "logistic_regression");
  const field = "mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm text-slate-100 focus-visible:outline-2 focus-visible:outline-cyan-400";
  return <div className="space-y-6">
    <header><p className="text-xs uppercase tracking-widest text-cyan-300">Machine learning · Deep learning</p>
      <h1 className="mt-2 text-3xl font-semibold">Model experiments</h1>
      <p className="mt-2 max-w-3xl text-sm text-slate-400">Train reproducible classifiers from cleaned operational datasets, compare maintained pipelines with a readable NumPy baseline, and retain evaluation evidence.</p></header>
    {error ? <p role="alert" className="rounded-lg border border-rose-400/30 p-4 text-sm text-rose-200">{error}</p> : null}
    <div className="grid gap-6 xl:grid-cols-[1fr_1.3fr]">
      <Card className="min-w-0 p-5"><h2 className="text-lg font-semibold">Run model comparison</h2>
        <p className="mt-2 text-xs text-slate-400">Uses cost above the training-row median as the demonstration target. Requests, day, and service are features; cost is excluded to prevent direct target leakage.</p>
        <form className="mt-4 space-y-4" onSubmit={train}>
          <label className="block text-xs text-slate-300">Experiment name<input className={field} required minLength={2} maxLength={120} value={name} onChange={(event) => setName(event.target.value)} /></label>
          <label className="block text-xs text-slate-300">Comparison suite<select className={field} disabled={training} value={suite} onChange={(event) => setSuite(event.target.value as "classical" | "neural" | "frameworks")}>
            <option value="classical">Classical · three baselines</option>
            <option value="neural">Neural · PyTorch MLP + three baselines</option>
            <option value="frameworks">Frameworks · PyTorch + TensorFlow/Keras</option>
          </select></label>
          {suite !== "classical" ? <p className="text-xs text-slate-400">CPU comparison · 80 epochs · 20–2,000 rows · at most 32 services · 90 second worker limit. Evaluation uses the same untouched holdout as the baselines.</p> : null}
          <label className="block text-xs text-slate-300">Saved dataset<select className={field} required value={datasetId} onChange={(event) => setDatasetId(event.target.value)}>
            <option value="" disabled>Select a dataset</option>{datasets.map((item) => <option key={item.id} value={item.id} disabled={item.valid_rows < 20}>{item.name} · {item.valid_rows} rows{item.valid_rows < 20 ? " · needs 20" : ""}</option>)}</select></label>
          <Button type="submit" disabled={training || loading || !datasetId}>{training ? "Training models…" : "Run experiment"}</Button>
          {training ? <p role="status" className="text-xs text-cyan-200">Fitting pipelines and evaluating the untouched holdout…</p> : null}
        </form>
        {!loading && !datasets.some((item) => item.valid_rows >= 20) ? <p className="mt-4 text-xs text-amber-200">Import a dataset with at least 20 rows before training. Both target classes also need five examples.</p> : null}
      </Card>
      <Card className="min-w-0 p-5"><h2 className="text-lg font-semibold">Experiment history</h2>
        {loading ? <p role="status" className="mt-4 text-sm text-slate-400">Loading experiment evidence…</p> : null}
        {!loading && catalog.length === 0 ? <p className="mt-4 text-sm text-slate-400">No experiments yet. Run the first comparison from a saved dataset.</p> : null}
        <ul className="mt-4 max-h-80 space-y-2 overflow-y-auto">{catalog.map((item) => <li key={item.id}><button type="button" disabled={training} onClick={() => void inspect(item.id)} className="flex w-full items-center justify-between gap-3 rounded-lg border border-white/10 p-3 text-left text-sm hover:bg-white/5 focus-visible:outline-2 focus-visible:outline-cyan-400">
          <span className="min-w-0"><span className="block truncate">{item.name}</span><span className="block truncate text-[10px] text-slate-500">{item.dataset_name} · best {displayModel(item.best_model)}</span></span>
          <Badge>{(item.best_balanced_accuracy * 100).toFixed(0)}%</Badge>
        </button></li>)}</ul>
      </Card>
    </div>
    {report && selected ? <section aria-label="Experiment report" className="space-y-6">
      <div><h2 className="text-xl font-semibold">{selected.name} · evaluation</h2><p className="mt-2 text-xs text-slate-400">{selected.dataset_name} · {report.target_definition} · scikit-learn {report.sklearn_version}</p></div>
      <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">{[
        ["Training rows", report.training_rows], ["Holdout rows", report.test_rows],
        ["Positive rate", `${(report.positive_rate * 100).toFixed(1)}%`], ["Random seed", report.random_seed],
      ].map(([label, value]) => <Card className="p-4" key={label}><dt className="text-xs text-slate-400">{label}</dt><dd className="mt-2 text-2xl">{value}</dd></Card>)}</dl>
      <Card className="overflow-x-auto p-5"><table className="w-full text-left text-xs"><caption className="mb-4 text-left text-sm font-semibold">Same holdout · model comparison</caption><thead><tr>{["Model", "Implementation", "Balanced accuracy", "Precision", "Recall", "F1", "ROC AUC", "Fit (ms)"].map((label) => <th className="p-2" scope="col" key={label}>{label}</th>)}</tr></thead><tbody>{report.models.map((model) => <tr className="border-t border-white/10" key={model.model}><th className="p-2 capitalize" scope="row">{displayModel(model.model)}</th><td className="p-2">{model.implementation}</td><td className="p-2">{(model.metrics.balanced_accuracy * 100).toFixed(1)}%</td><td className="p-2">{model.metrics.precision.toFixed(2)}</td><td className="p-2">{model.metrics.recall.toFixed(2)}</td><td className="p-2">{model.metrics.f1.toFixed(2)}</td><td className="p-2">{model.metrics.roc_auc.toFixed(2)}</td><td className="p-2">{model.fit_ms.toFixed(2)}</td></tr>)}</tbody></table></Card>
      {report.models.filter((model) => model.training_curve.length > 0).map((model) => {
        const maximum = Math.max(...model.training_curve.map((point) => point.loss), 0.001);
        const points = model.training_curve.map((point, i) => `${i * 600 / 79},${120 - point.loss / maximum * 110}`).join(" ");
        return <Card className="min-w-0 p-5" key={model.model}>
          <h3 className="font-semibold">{displayModel(model.model)} · training loss</h3>
          <p className="mt-2 text-xs text-slate-400">PyTorch {report.torch_version} · binary cross entropy · fixed epochs; holdout never selects the stopping point.</p>
          <svg className="mt-4 h-40 w-full" viewBox="0 0 600 130" role="img" aria-label={`Training loss from ${model.training_curve[0].loss.toFixed(4)} to ${model.training_curve.at(-1)!.loss.toFixed(4)} over 80 epochs`}>
            <polyline points={points} fill="none" stroke="currentColor" strokeWidth="2" className="text-cyan-300" />
          </svg>
          <details className="mt-3 text-xs"><summary className="cursor-pointer">Inspect epoch values</summary>
            <div className="mt-2 max-h-48 overflow-auto"><table className="w-full text-left"><caption className="sr-only">Training loss by epoch</caption><thead><tr><th scope="col">Epoch</th><th scope="col">Loss</th></tr></thead><tbody>{model.training_curve.map((point) => <tr key={point.epoch}><th scope="row">{point.epoch}</th><td>{point.loss.toFixed(5)}</td></tr>)}</tbody></table></div>
          </details>
        </Card>;
      })}
      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-5"><h3 className="font-semibold">Logistic confusion matrix</h3><p className="mt-2 text-xs text-slate-400">Rows are actual class; columns are predicted class.</p>
          {logistic ? <table className="mt-4 w-full text-center text-sm"><thead><tr><th></th><th className="p-2" scope="col">Predicted normal</th><th className="p-2" scope="col">Predicted high</th></tr></thead><tbody>{logistic.metrics.confusion_matrix.map((row, index) => <tr className="border-t border-white/10" key={index}><th className="p-2 text-left" scope="row">Actual {index ? "high" : "normal"}</th>{row.map((value, column) => <td className="p-2 text-xl" key={column}>{value}</td>)}</tr>)}</tbody></table> : null}
        </Card>
        <Card className="p-5"><h3 className="font-semibold">Permutation effects</h3><p className="mt-2 text-xs text-slate-400">Balanced-accuracy decrease after shuffling one input, repeated eight times.</p>
          <div role="img" aria-label="Permutation feature effects on holdout balanced accuracy" className="mt-5 space-y-4">{report.feature_effects.map((effect) => <div key={effect.feature}><div className="flex justify-between text-xs"><span className="capitalize">{effect.feature}</span><span>{effect.importance_mean.toFixed(3)} ± {effect.importance_stddev.toFixed(3)}</span></div><div className="mt-1 h-2 rounded bg-white/10"><div className="h-full rounded bg-cyan-400" style={{ width: `${Math.min(100, Math.max(2, Math.abs(effect.importance_mean) * 200))}%` }} /></div></div>)}</div>
        </Card>
      </div>
      <Card className="p-5"><h3 className="font-semibold">Evaluation limits</h3><ul className="mt-3 space-y-2 text-xs text-slate-400">{report.caveats.map((item) => <li key={item}>{item}</li>)}</ul></Card>
    </section> : null}
  </div>;
}
