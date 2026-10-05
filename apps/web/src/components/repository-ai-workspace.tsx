"use client";

import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  repositoryCatalogSchema,
  repositoryAIOperationsSchema,
  repositoryExplanationSchema,
  repositoryProviderHealthSchema,
  repositoryPromptVersionSchema,
  repositoryPromptVersionsSchema,
  repositoryRetrievalEvaluationSchema,
  repositoryRetrievalSchema,
  type RepositoryExplanation,
  type RepositoryAIOperations,
  type RepositoryFile,
  type RepositoryProviderHealth,
  type RepositoryPromptVersion,
  type RepositoryRetrieval,
  type RepositoryRetrievalEvaluation,
} from "@/lib/repository-ai";

async function responseBody(response: Response): Promise<unknown> {
  const body: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof body === "object" && body !== null && "detail" in body
      && typeof body.detail === "string" ? body.detail : "Repository request failed.";
    throw new Error(detail);
  }
  return body;
}

export function RepositoryAIWorkspace() {
  const [files, setFiles] = useState<RepositoryFile[]>([]);
  const [path, setPath] = useState("");
  const [startLine, setStartLine] = useState(1);
  const [endLine, setEndLine] = useState(40);
  const [intent, setIntent] = useState("explain");
  const [tier, setTier] = useState("auto");
  const [provider, setProvider] = useState("auto");
  const [providers, setProviders] = useState<RepositoryProviderHealth[]>([]);
  const [operations, setOperations] = useState<RepositoryAIOperations | null>(null);
  const [prompts, setPrompts] = useState<RepositoryPromptVersion[]>([]);
  const [promptVersionId, setPromptVersionId] = useState("");
  const [instruction, setInstruction] = useState("Explain every line, keyword, and relationship in this slice.");
  const [report, setReport] = useState<RepositoryExplanation | null>(null);
  const [retrievalQuery, setRetrievalQuery] = useState("provider stream structured validation");
  const [retrievalMode, setRetrievalMode] = useState("hybrid");
  const [retrieval, setRetrieval] = useState<RepositoryRetrieval | null>(null);
  const [retrievalEvaluation, setRetrievalEvaluation] = useState<RepositoryRetrievalEvaluation | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [retrieving, setRetrieving] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [streamPreview, setStreamPreview] = useState("");
  const [error, setError] = useState("");
  const active = useRef<AbortController | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      fetch("/api/ai/repository", { cache: "no-store", signal: controller.signal }).then(responseBody),
      fetch("/api/ai/repository/providers", { cache: "no-store", signal: controller.signal }).then(responseBody),
      fetch("/api/ai/repository/prompts", { cache: "no-store", signal: controller.signal }).then(responseBody),
      fetch("/api/ai/repository/operations", { cache: "no-store", signal: controller.signal }).then(responseBody),
    ])
      .then(([catalogBody, providerBody, promptBody, operationsBody]) => {
        const catalog = repositoryCatalogSchema.parse(catalogBody);
        setFiles(catalog);
        setProviders(repositoryProviderHealthSchema.parse(providerBody));
        setPrompts(repositoryPromptVersionsSchema.parse(promptBody));
        setOperations(repositoryAIOperationsSchema.parse(operationsBody));
        const preferred = catalog.find((item) => item.path.endsWith("repository_ai.py")) ?? catalog[0];
        if (preferred) {
          setPath(preferred.path);
          setEndLine(Math.min(40, preferred.lines));
        }
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : "Repository catalog unavailable.");
        }
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => { controller.abort(); active.current?.abort(); };
  }, []);

  const selectedFile = useMemo(() => files.find((item) => item.path === path), [files, path]);

  function chooseFile(nextPath: string) {
    setPath(nextPath);
    const file = files.find((item) => item.path === nextPath);
    setStartLine(1);
    setEndLine(Math.min(40, file?.lines ?? 40));
    setReport(null);
  }

  async function explain(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    active.current?.abort();
    const controller = new AbortController();
    active.current = controller;
    setRunning(true);
    setError("");
    setStreamPreview("");
    setReport(null);
    try {
      const response = await fetch("/api/ai/repository/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          path,
          start_line: startLine,
          end_line: endLine,
          intent,
          tier,
          provider,
          instruction,
          prompt_version_id: promptVersionId || null,
        }),
        signal: controller.signal,
      });
      if (!response.ok || !response.body) {
        await responseBody(response);
        throw new Error("Repository stream did not start.");
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let receivedResult = false;
      while (true) {
        const chunk = await reader.read();
        buffer += decoder.decode(chunk.value ?? new Uint8Array(), { stream: !chunk.done });
        const frames = buffer.split("\n\n");
        buffer = frames.pop() ?? "";
        for (const frame of frames) {
          const event = frame.split("\n").find((line) => line.startsWith("event: "))?.slice(7);
          const data = frame.split("\n").find((line) => line.startsWith("data: "))?.slice(6);
          if (!event || !data) continue;
          const payload: unknown = JSON.parse(data);
          if (event === "delta" && typeof payload === "object" && payload !== null && "delta" in payload && typeof payload.delta === "string") {
            setStreamPreview((current) => (current + payload.delta).slice(-2_000));
          } else if (event === "result") {
            setReport(repositoryExplanationSchema.parse(payload));
            receivedResult = true;
          } else if (event === "error" && typeof payload === "object" && payload !== null && "detail" in payload && typeof payload.detail === "string") {
            throw new Error(payload.detail);
          }
        }
        if (chunk.done) break;
      }
      if (!receivedResult) throw new Error("Repository stream ended before a validated result.");
    } catch (reason) {
      if (!controller.signal.aborted) {
        setError(reason instanceof Error ? reason.message : "Repository explanation failed.");
      }
    } finally {
      if (!controller.signal.aborted) setRunning(false);
    }
  }

  async function savePromptVersion() {
    setError("");
    try {
      const body = await responseBody(await fetch("/api/ai/repository/prompts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt_key: "repository-explanation",
          name: "Repository explanation",
          instruction,
        }),
      }));
      const saved = repositoryPromptVersionSchema.parse(body);
      setPrompts((current) => [saved, ...current]);
      setPromptVersionId(saved.id);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Prompt version could not be saved.");
    }
  }

  async function searchRepository(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRetrieving(true);
    setError("");
    try {
      const body = await responseBody(await fetch("/api/ai/repository/retrieval", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: retrievalQuery, top_k: 6, mode: retrievalMode }),
      }));
      setRetrieval(repositoryRetrievalSchema.parse(body));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Repository retrieval failed.");
    } finally {
      setRetrieving(false);
    }
  }

  async function runRetrievalEvaluation() {
    setEvaluating(true);
    setError("");
    try {
      const body = await responseBody(await fetch("/api/ai/repository/retrieval/evaluations", {
        method: "POST",
      }));
      setRetrievalEvaluation(repositoryRetrievalEvaluationSchema.parse(body));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Retrieval evaluation failed.");
    } finally {
      setEvaluating(false);
    }
  }

  function openCitation(citation: RepositoryRetrieval["hits"][number]["citation"]) {
    if (!files.some((item) => item.path === citation.path)) return;
    setPath(citation.path);
    setStartLine(citation.start_line);
    setEndLine(Math.min(citation.end_line, citation.start_line + 119));
    setReport(null);
  }

  return <div className="space-y-6">
    <header className="border-b border-white/[.08] pb-6">
      <p className="text-[10px] font-bold uppercase tracking-[.2em] text-violet-300">AI engineering · Phase 8</p>
      <h1 className="mt-2 text-3xl font-semibold">Repository code intelligence</h1>
      <p className="mt-3 max-w-4xl text-sm leading-relaxed text-slate-400">
        Source remains unchanged on the left; explanations stay beside it on the right. Economy mode uses the lowest-cost configured model for explanation, while balanced mode routes review and change planning to the stronger coding model.
      </p>
    </header>

    {error ? <p role="alert" className="rounded-lg border border-rose-400/30 bg-rose-400/[.05] p-4 text-sm text-rose-200">{error}</p> : null}

    <Card className="p-5">
      {operations ? <div className="mb-5 grid gap-3 sm:grid-cols-2" aria-label="AI operational controls">
        <div className="rounded-lg border border-white/[.08] bg-slate-950/35 p-3"><div className="flex items-center justify-between gap-3"><span className="text-xs font-semibold">Monthly inference budget</span><Badge tone={operations.budget.remaining_usd > 0 ? "success" : "danger"}>${operations.budget.remaining_usd.toFixed(2)} left</Badge></div><p className="mt-2 text-[10px] text-slate-500">${operations.budget.committed_usd.toFixed(2)} committed · ${operations.budget.reserved_usd.toFixed(2)} reserved · ${operations.budget.monthly_limit_usd.toFixed(2)} limit</p></div>
        <div className="rounded-lg border border-white/[.08] bg-slate-950/35 p-3"><div className="flex items-center justify-between gap-3"><span className="text-xs font-semibold">Rolling inference SLO</span><Badge tone={operations.slo.availability_met === false || operations.slo.latency_met === false ? "danger" : operations.slo.sample_count ? "success" : "neutral"}>{operations.slo.sample_count ? `${Math.round((operations.slo.availability ?? 0) * 100)}% available` : "Awaiting samples"}</Badge></div><p className="mt-2 text-[10px] text-slate-500">p95 {operations.slo.p95_seconds === null ? "—" : `${operations.slo.p95_seconds.toFixed(2)} s`} · targets {(operations.slo.availability_target * 100).toFixed(0)}% / {operations.slo.p95_seconds_target.toFixed(0)} s</p></div>
      </div> : null}
      <div className="mb-5 grid gap-3 sm:grid-cols-2" aria-label="Inference provider health">
        {providers.map((item) => <div key={item.provider} className="rounded-lg border border-white/[.08] bg-slate-950/35 p-3">
          <div className="flex items-center justify-between gap-3"><span className="text-xs font-semibold capitalize">{item.provider}</span><Badge tone={item.reachable ? "success" : "neutral"}>{item.detail}</Badge></div>
          <p className="mt-2 text-[10px] text-slate-500">{item.model}{item.latency_ms !== null ? ` · ${item.latency_ms} ms` : ""}</p>
        </div>)}
      </div>
      <form className="grid gap-4 lg:grid-cols-6" onSubmit={explain}>
        <label className="lg:col-span-3 text-xs text-slate-300">Repository file
          <select aria-label="Repository file" disabled={loading || running} value={path} onChange={(event) => chooseFile(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm focus-visible:outline-2 focus-visible:outline-violet-400">
            {files.map((file) => <option key={file.path} value={file.path}>{file.path}</option>)}
          </select>
        </label>
        <label className="text-xs text-slate-300">Start line
          <input aria-label="Start line" type="number" min={1} max={selectedFile?.lines ?? 1} value={startLine} onChange={(event) => setStartLine(Number(event.target.value))} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/>
        </label>
        <label className="text-xs text-slate-300">End line
          <input aria-label="End line" type="number" min={startLine} max={Math.min(selectedFile?.lines ?? 120, startLine + 119)} value={endLine} onChange={(event) => setEndLine(Number(event.target.value))} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/>
        </label>
        <label className="text-xs text-slate-300">Task
          <select aria-label="Task" value={intent} onChange={(event) => setIntent(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm">
            <option value="explain">Explain</option><option value="review">Review</option><option value="change_plan">Change plan</option>
          </select>
        </label>
        <label className="text-xs text-slate-300">Cost route
          <select aria-label="Cost route" value={tier} onChange={(event) => setTier(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm">
            <option value="auto">Auto</option><option value="economy">Economy</option><option value="balanced">Balanced</option>
          </select>
        </label>
        <label className="text-xs text-slate-300">Provider
          <select aria-label="Provider" value={provider} onChange={(event) => setProvider(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm">
            <option value="auto">Auto</option><option value="openai">OpenAI</option><option value="local">Local</option>
          </select>
        </label>
        <label className="lg:col-span-2 text-xs text-slate-300">Prompt version
          <select aria-label="Prompt version" value={promptVersionId} onChange={(event) => {
            setPromptVersionId(event.target.value);
            const selected = prompts.find((item) => item.id === event.target.value);
            if (selected) setInstruction(selected.instruction);
          }} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm">
            <option value="">Inline draft</option>
            {prompts.map((item) => <option key={item.id} value={item.id}>{item.name} · v{item.version}</option>)}
          </select>
        </label>
        <label className="lg:col-span-3 text-xs text-slate-300">Instruction
          <input aria-label="Instruction" minLength={3} maxLength={500} required value={instruction} onChange={(event) => setInstruction(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/>
        </label>
        <div className="flex items-end gap-2 lg:col-span-1"><Button disabled={running || instruction.trim().length < 10} type="button" onClick={savePromptVersion}>Save v</Button><Button disabled={loading || running || !path} type="submit">{running ? "Explaining…" : "Explain source"}</Button></div>
        {running ? <p role="status" className="lg:col-span-6 text-xs text-violet-200">Generating a structured side-by-side explanation without granting model tools or write access…</p> : null}
      </form>
      {running && streamPreview ? <pre aria-label="Streaming structured output" className="mt-4 max-h-28 overflow-hidden whitespace-pre-wrap break-all rounded-lg border border-violet-300/15 bg-violet-300/[.03] p-3 text-[10px] text-violet-200">{streamPreview}</pre> : null}
    </Card>

    <Card className="p-5">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[.16em] text-cyan-300">Grounded retrieval</p>
          <h2 className="mt-1 font-semibold">Find exact repository evidence</h2>
          <p className="mt-2 max-w-3xl text-xs leading-5 text-slate-400">Hybrid ranking combines lexical overlap with a deterministic local embedding baseline. Every result is pinned to a file hash and exact line range before it can become model context.</p>
        </div>
        <Button type="button" variant="secondary" disabled={evaluating} onClick={runRetrievalEvaluation}>{evaluating ? "Evaluating…" : "Run regression evaluation"}</Button>
      </div>
      <form className="mt-5 grid gap-3 md:grid-cols-[minmax(0,1fr)_10rem_auto]" onSubmit={searchRepository}>
        <label className="text-xs text-slate-300">Retrieval query
          <input aria-label="Retrieval query" minLength={3} maxLength={300} required value={retrievalQuery} onChange={(event) => setRetrievalQuery(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/>
        </label>
        <label className="text-xs text-slate-300">Ranking
          <select aria-label="Retrieval ranking" value={retrievalMode} onChange={(event) => setRetrievalMode(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"><option value="hybrid">Hybrid</option><option value="lexical">Lexical</option></select>
        </label>
        <div className="flex items-end"><Button type="submit" disabled={retrieving || retrievalQuery.trim().length < 3}>{retrieving ? "Searching…" : "Search repository"}</Button></div>
      </form>
      {retrieval ? <section aria-label="Repository retrieval results" className="mt-5 space-y-3">
        <div className="flex flex-wrap gap-2"><Badge tone="info">{retrieval.mode}</Badge><Badge>{retrieval.embedding_provider}</Badge><Badge>{retrieval.indexed_files} files</Badge><Badge>{retrieval.indexed_chunks} chunks</Badge><Badge>{retrieval.cache_hits} cache hits</Badge>{retrieval.truncated ? <Badge tone="warning">Bound reached</Badge> : null}</div>
        {retrieval.hits.length === 0 ? <p className="rounded-lg border border-white/[.08] p-4 text-xs text-slate-400">No matching source chunks were found.</p> : retrieval.hits.map((hit) => <article key={hit.citation.id} className="rounded-lg border border-white/[.08] bg-slate-950/35 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3"><div><h3 className="font-mono text-xs text-cyan-200">{hit.citation.path}:{hit.citation.start_line}-{hit.citation.end_line}</h3><p className="mt-1 text-[10px] text-slate-500">Citation {hit.citation.id} · score {hit.final_score.toFixed(3)} · lexical {hit.lexical_score.toFixed(3)} · embedding {hit.embedding_score.toFixed(3)}</p></div><div className="flex items-center gap-2">{hit.prompt_injection_signals.length ? <Badge tone="danger">Untrusted instruction signal</Badge> : <Badge tone="success">Content scan clear</Badge>}<Button type="button" variant="ghost" onClick={() => openCitation(hit.citation)}>Open cited lines</Button></div></div>
          <pre className="mt-3 max-h-52 overflow-auto whitespace-pre-wrap rounded-lg border border-white/[.06] bg-slate-950 p-3 text-[11px] leading-5 text-slate-300"><code>{hit.snippet}</code></pre>
        </article>)}
      </section> : null}
      {retrievalEvaluation ? <section aria-label="Retrieval evaluation" className="mt-5 rounded-lg border border-white/[.08] p-4">
        <div className="flex flex-wrap items-center gap-2"><strong className="text-xs">{retrievalEvaluation.name}</strong><Badge tone={retrievalEvaluation.report.grounding_passed ? "success" : "danger"}>Grounding</Badge><Badge tone={retrievalEvaluation.report.citation_accuracy === 1 ? "success" : "danger"}>{Math.round(retrievalEvaluation.report.citation_accuracy * 100)}% citations</Badge><Badge tone={retrievalEvaluation.report.injection_detection_passed ? "success" : "danger"}>Injection fixture</Badge></div>
        <p className="mt-2 text-[10px] text-slate-500">Immutable run {retrievalEvaluation.id} · {new Date(retrievalEvaluation.created_at).toLocaleString()}</p>
      </section> : null}
    </Card>

    {!loading && files.length === 0 ? <Card className="p-8 text-center text-sm text-slate-400">No allowlisted source files are available.</Card> : null}

    {report ? <section aria-label="Repository explanation" className="space-y-4">
      <Card className="p-5">
        <div className="flex flex-wrap items-start justify-between gap-4"><div><h2 className="font-semibold">{report.file.path}</h2><p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-300">{report.overview}</p></div><div className="flex flex-wrap gap-2"><Badge>{report.provider}</Badge>{report.fallback_from ? <Badge tone="warning">Fallback from {report.fallback_from}</Badge> : null}<Badge>{report.model}</Badge><Badge>{report.usage.input_tokens + report.usage.output_tokens} tokens</Badge><Badge>${report.usage.estimated_cost_usd.toFixed(6)}</Badge></div></div>
        {report.architecture_relations.length ? <ul className="mt-4 space-y-1 text-xs text-slate-400">{report.architecture_relations.map((relation) => <li key={relation}>↳ {relation}</li>)}</ul> : null}
        {report.suggested_change ? <div className="mt-4 rounded-lg border border-amber-300/20 bg-amber-300/[.04] p-4 text-sm text-amber-100"><strong>Proposed change:</strong> {report.suggested_change}</div> : null}
      </Card>
      <div className="overflow-hidden rounded-xl border border-white/[.09]" role="table" aria-label="Code with side explanations">
        <div className="hidden grid-cols-[minmax(0,1.05fr)_minmax(0,.95fr)] bg-white/[.04] text-[10px] font-bold uppercase tracking-wider text-slate-500 md:grid"><div className="border-r border-white/[.08] px-4 py-3">Source code</div><div className="px-4 py-3">Side explanation</div></div>
        {report.lines.map((line) => <div key={line.line_number} role="row" className="grid border-t border-white/[.07] first:border-t-0 md:grid-cols-[minmax(0,1.05fr)_minmax(0,.95fr)]">
          <div role="cell" className="min-w-0 border-white/[.08] bg-slate-950/40 px-4 py-3 md:border-r"><pre className="overflow-x-auto whitespace-pre-wrap break-words text-xs leading-6"><span className="mr-4 select-none text-slate-600">{line.line_number}</span><code>{line.code || " "}</code></pre></div>
          <div role="cell" className="min-w-0 px-4 py-3"><p className="text-xs leading-5 text-slate-300">{line.explanation}</p>{line.keywords.length ? <dl className="mt-2 space-y-1">{line.keywords.map((keyword) => <div key={`${line.line_number}-${keyword.token}`} className="text-[10px]"><dt className="inline font-mono text-cyan-300">{keyword.token}</dt><dd className="inline text-slate-500"> — {keyword.meaning}</dd></div>)}</dl> : null}{line.relations.length ? <ul className="mt-2 space-y-1 text-[10px] text-violet-300">{line.relations.map((relation) => <li key={relation}>↳ {relation}</li>)}</ul> : null}</div>
        </div>)}
      </div>
    </section> : null}
  </div>;
}
