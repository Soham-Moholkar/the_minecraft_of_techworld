"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  repositoryCatalogSchema,
  repositoryPatchProposalSchema,
  repositoryPatchProposalsSchema,
  repositoryPatchWorkflowSchema,
  repositoryPatchWorkflowsSchema,
  repositoryWorkflowReplaySchema,
  repositoryTestProfilesSchema,
  repositoryTestRunSchema,
  repositoryTestRunsSchema,
  type RepositoryFile,
  type RepositoryPatchProposal,
  type RepositoryPatchWorkflow,
  type RepositoryWorkflowReplay,
  type RepositoryTestProfile,
  type RepositoryTestRun,
} from "@/lib/repository-ai";

async function body(response: Response): Promise<unknown> {
  const payload: unknown = await response.json();
  if (!response.ok) {
    const detail = typeof payload === "object" && payload !== null && "detail" in payload
      && typeof payload.detail === "string" ? payload.detail : "Patch request failed.";
    throw new Error(detail);
  }
  return payload;
}

/** Inspect a verified snapshot; stepping between frames has no API mutation. */
function WorkflowReplayPanel({
  replay, cursor, onCursor,
}: {
  replay: RepositoryWorkflowReplay;
  cursor: number;
  onCursor: (next: number) => void;
}) {
  const frame = replay.frames[cursor];
  if (!frame) return null;
  const outgoing = replay.graph.edges.filter((edge) => edge.source === frame.event.state);

  return <div aria-label={`Workflow replay ${replay.workflow_id}`} className="mt-4 space-y-3 rounded-lg border border-violet-300/20 bg-slate-950/50 p-4">
    <p className="text-xs text-slate-300">
      Policy graph v{replay.graph.version} · {replay.frames.length} persisted events · final state {replay.final_state}
    </p>
    {/* Every node comes from the server's fixed policy, including the single
        guarded tool. Highlight the state reached by the selected event. */}
    <ol aria-label="Policy graph nodes" className="flex flex-wrap gap-2">
      {replay.graph.nodes.map((node) => <li key={node.state} className={`rounded border px-2 py-1 text-xs ${node.state === frame.event.state ? "border-violet-300 text-violet-200" : "border-white/10 text-slate-400"}`}>
        {node.title} · {node.tool ?? node.kind}
      </li>)}
    </ol>
    {/* Branches describe policy choices, not buttons. Privileged work still goes
        through the existing exact-digest approval routes elsewhere on the page. */}
    {outgoing.length > 0 ? <ul aria-label="Available policy branches" className="grid gap-1 text-xs text-slate-400">
      {outgoing.map((edge) => <li key={`${edge.source}-${edge.condition}`}>
        {edge.condition} → {edge.target} · {edge.authority}
      </li>)}
    </ul> : null}
    <div className="flex items-center gap-2">
      <Button variant="secondary" disabled={cursor === 0} onClick={() => onCursor(cursor - 1)}>Previous event</Button>
      <span className="text-xs text-slate-400">{cursor + 1} / {replay.frames.length}</span>
      <Button variant="secondary" disabled={cursor >= replay.frames.length - 1} onClick={() => onCursor(cursor + 1)}>Next event</Button>
    </div>
    <div aria-live="polite" className="rounded border border-white/10 p-3 text-xs text-slate-300">
      <p className="font-semibold text-cyan-300">{frame.event.step} · {frame.kind}</p>
      <p className="mt-1">{frame.event.detail}</p>
      <p className="mt-2 text-slate-400">Branch: {frame.condition ?? "recorded evidence"} · authority: {frame.authority}</p>
    </div>
  </div>;
}

export function RepositoryPatchWorkspace() {
  const [files, setFiles] = useState<RepositoryFile[]>([]);
  const [path, setPath] = useState("");
  const [startLine, setStartLine] = useState(1);
  const [endLine, setEndLine] = useState(1);
  const [replacement, setReplacement] = useState("");
  const [summary, setSummary] = useState("Replace the reviewed source range");
  const [rationale, setRationale] = useState("Apply a bounded change through exact-diff human approval.");
  const [objective, setObjective] = useState("Produce a validated patch proposal while preserving explicit human approval.");
  const [proposals, setProposals] = useState<RepositoryPatchProposal[]>([]);
  const [workflows, setWorkflows] = useState<RepositoryPatchWorkflow[]>([]);
  const [testProfiles, setTestProfiles] = useState<RepositoryTestProfile[]>([]);
  const [testRuns, setTestRuns] = useState<RepositoryTestRun[]>([]);
  const [replay, setReplay] = useState<RepositoryWorkflowReplay | null>(null);
  const [replayCursor, setReplayCursor] = useState(0);
  const [testProfileId, setTestProfileId] = useState("api-agent-boundary");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    Promise.all([
      fetch("/api/ai/repository", { cache: "no-store", signal: controller.signal }).then(body),
      fetch("/api/ai/repository/patches", { cache: "no-store", signal: controller.signal }).then(body),
      fetch("/api/ai/repository/workflows", { cache: "no-store", signal: controller.signal }).then(body),
      fetch("/api/ai/repository/test-profiles", { cache: "no-store", signal: controller.signal }).then(body),
      fetch("/api/ai/repository/test-runs", { cache: "no-store", signal: controller.signal }).then(body),
    ]).then(([catalogBody, proposalsBody, workflowsBody, profilesBody, runsBody]) => {
      const catalog = repositoryCatalogSchema.parse(catalogBody);
      setFiles(catalog);
      setProposals(repositoryPatchProposalsSchema.parse(proposalsBody));
      setWorkflows(repositoryPatchWorkflowsSchema.parse(workflowsBody));
      const profiles = repositoryTestProfilesSchema.parse(profilesBody);
      setTestProfiles(profiles);
      setTestRuns(repositoryTestRunsSchema.parse(runsBody));
      if (profiles[0]) setTestProfileId(profiles[0].id);
      if (catalog[0]) setPath(catalog[0].path);
    }).catch((reason: unknown) => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Patch workspace unavailable.");
    });
    return () => controller.abort();
  }, []);

  const selected = files.find((file) => file.path === path);

  async function propose(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selected) return;
    setBusy(true); setError("");
    try {
      const payload = await body(await fetch("/api/ai/repository/patches", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path, expected_sha256: selected.sha256, start_line: startLine, end_line: endLine, replacement, summary, rationale }),
      }));
      const proposal = repositoryPatchProposalSchema.parse(payload);
      setProposals((current) => [proposal, ...current]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Patch proposal failed.");
    } finally { setBusy(false); }
  }

  async function startWorkflow() {
    if (!selected) return;
    setBusy(true); setError("");
    try {
      const payload = await body(await fetch("/api/ai/repository/workflows", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objective,
          plan: { path, expected_sha256: selected.sha256, start_line: startLine, end_line: endLine, replacement, summary, rationale },
        }),
      }));
      const workflow = repositoryPatchWorkflowSchema.parse(payload);
      setWorkflows((current) => [workflow, ...current]);
      setReplay(null);
      if (workflow.proposal) setProposals((current) => [workflow.proposal!, ...current]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Patch workflow failed.");
    } finally { setBusy(false); }
  }

  async function transition(proposal: RepositoryPatchProposal, action: "approve" | "rollback") {
    setBusy(true); setError("");
    try {
      const payload = await body(await fetch(`/api/ai/repository/patches/${proposal.id}/${action}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          proposal_digest: proposal.proposal_digest,
          confirmation: action === "approve" ? "APPLY EXACT PATCH" : "ROLL BACK EXACT PATCH",
        }),
      }));
      const updated = repositoryPatchProposalSchema.parse(payload);
      setProposals((current) => current.map((item) => item.id === updated.id ? updated : item));
      setReplay(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Patch transition failed.");
    } finally { setBusy(false); }
  }

  async function requestTests(proposal: RepositoryPatchProposal) {
    setBusy(true); setError("");
    try {
      const payload = await body(await fetch(`/api/ai/repository/patches/${proposal.id}/test-runs`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ profile_id: testProfileId }),
      }));
      const run = repositoryTestRunSchema.parse(payload);
      setTestRuns((current) => [run, ...current]);
      appendWorkflowEvidence(
        proposal.id,
        "test_requested",
        `Test profile ${run.profile_id} attempt ${run.attempt} awaits separate approval.`,
      );
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Test run request failed.");
    } finally { setBusy(false); }
  }

  async function transitionTest(run: RepositoryTestRun, action: "approve" | "cancel") {
    setBusy(true); setError("");
    try {
      const payload = await body(await fetch(`/api/ai/repository/test-runs/${run.id}/${action}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: action === "approve" ? JSON.stringify({
          run_digest: run.run_digest,
          confirmation: "RUN ISOLATED TEST PROFILE",
        }) : undefined,
      }));
      const updated = repositoryTestRunSchema.parse(payload);
      setTestRuns((current) => current.map((item) => item.id === updated.id ? updated : item));
      appendWorkflowEvidence(
        run.proposal_id,
        action === "approve" ? "test_queued" : updated.status === "cancelled" ? "test_cancelled" : "test_cancel_requested",
        action === "approve"
          ? `Approved test attempt ${updated.attempt} entered the isolated worker queue.`
          : `Operator cancellation recorded for test attempt ${updated.attempt}.`,
      );
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Test run transition failed.");
    } finally { setBusy(false); }
  }

  async function retryTest(run: RepositoryTestRun) {
    setBusy(true); setError("");
    try {
      const payload = await body(await fetch(`/api/ai/repository/test-runs/${run.id}/retry`, {
        method: "POST",
      }));
      const retry = repositoryTestRunSchema.parse(payload);
      setTestRuns((current) => [retry, ...current]);
      appendWorkflowEvidence(
        run.proposal_id,
        "test_retry_requested",
        `Fresh test attempt ${retry.attempt} awaits a new execution approval.`,
      );
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Fresh test retry could not be created.");
    } finally { setBusy(false); }
  }

  function appendWorkflowEvidence(proposalId: string, step: string, detail: string) {
    // Replay is a point-in-time server projection. Invalidate it as soon as a
    // local mutation changes the visible event history, then load it afresh.
    setReplay(null);
    setWorkflows((current) => current.map((workflow) => workflow.proposal?.id === proposalId ? {
      ...workflow,
      updated_at: new Date().toISOString(),
      events: [...workflow.events, {
        state: workflow.status,
        step,
        at: new Date().toISOString(),
        detail,
      }],
    } : workflow));
  }

  async function refreshTestRuns() {
    setBusy(true); setError("");
    try {
      const [workflowPayload, runPayload] = await Promise.all([
        body(await fetch("/api/ai/repository/workflows", { cache: "no-store" })),
        body(await fetch("/api/ai/repository/test-runs", { cache: "no-store" })),
      ]);
      setWorkflows(repositoryPatchWorkflowsSchema.parse(workflowPayload));
      setTestRuns(repositoryTestRunsSchema.parse(runPayload));
      setReplay(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Test runs could not be refreshed.");
    } finally { setBusy(false); }
  }

  async function loadReplay(workflowId: string) {
    setBusy(true); setError("");
    try {
      const payload = await body(await fetch(`/api/ai/repository/workflows/${workflowId}/replay`, { cache: "no-store" }));
      const parsed = repositoryWorkflowReplaySchema.parse(payload);
      if (parsed.workflow_id !== workflowId) throw new Error("Replay did not match the selected workflow.");
      setReplay(parsed);
      setReplayCursor(parsed.frames.length - 1);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Workflow replay could not be loaded.");
    } finally { setBusy(false); }
  }

  return <section className="mt-6 space-y-4" aria-labelledby="patch-workflow-title">
    <header className="border-b border-white/[.08] pb-5">
      <p className="text-[10px] font-bold uppercase tracking-[.2em] text-amber-300">AI engineering · Phase 9</p>
      <h2 id="patch-workflow-title" className="mt-2 text-2xl font-semibold">Human-approved patch workflow</h2>
      <p className="mt-2 max-w-4xl text-sm leading-relaxed text-slate-400">Create one bounded replacement, review the server-generated diff and digest, and separately approve any isolated test profile. Test success records evidence only; it never applies, commits, pushes, or deploys a patch.</p>
    </header>
    {error ? <p role="alert" className="rounded-lg border border-rose-400/30 bg-rose-400/[.05] p-4 text-sm text-rose-200">{error}</p> : null}
    <Card className="p-5">
      <form onSubmit={propose} className="grid gap-4 lg:grid-cols-6">
        <label className="text-xs text-slate-300 lg:col-span-4">Existing allowlisted file<select aria-label="Patch file" value={path} onChange={(event) => { setPath(event.target.value); setStartLine(1); setEndLine(1); }} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm">{files.map((file) => <option key={file.path} value={file.path}>{file.path}</option>)}</select></label>
        <label className="text-xs text-slate-300">Start line<input aria-label="Patch start line" type="number" min={1} max={selected?.lines ?? 1} value={startLine} onChange={(event) => setStartLine(Number(event.target.value))} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/></label>
        <label className="text-xs text-slate-300">End line<input aria-label="Patch end line" type="number" min={startLine} max={selected?.lines ?? 1} value={endLine} onChange={(event) => setEndLine(Number(event.target.value))} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/></label>
        <label className="text-xs text-slate-300 lg:col-span-3">Summary<input aria-label="Patch summary" minLength={5} maxLength={200} value={summary} onChange={(event) => setSummary(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/></label>
        <label className="text-xs text-slate-300 lg:col-span-3">Rationale<input aria-label="Patch rationale" minLength={10} maxLength={2000} value={rationale} onChange={(event) => setRationale(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/></label>
        <label className="text-xs text-slate-300 lg:col-span-6">Workflow objective<input aria-label="Workflow objective" minLength={10} maxLength={500} value={objective} onChange={(event) => setObjective(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm"/></label>
        <label className="text-xs text-slate-300 lg:col-span-6">Exact replacement text<textarea aria-label="Patch replacement" rows={7} maxLength={100000} value={replacement} onChange={(event) => setReplacement(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 font-mono text-xs"/></label>
        <div className="flex flex-wrap gap-2 lg:col-span-6"><Button disabled={busy || !selected} type="button" onClick={startWorkflow}>{busy ? "Working…" : "Run deterministic workflow"}</Button><Button variant="secondary" disabled={busy || !selected} type="submit">Create proposal directly</Button></div>
      </form>
    </Card>
    {workflows.map((workflow) => <Card key={workflow.id} className="p-5">
      <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.16em] text-violet-300">Deterministic workflow</p><h3 className="mt-1 font-semibold">{workflow.objective}</h3></div><Badge tone={workflow.status === "applied" || workflow.status === "rolled_back" ? "success" : workflow.status === "failed" || workflow.status === "conflicted" ? "danger" : "warning"}>{workflow.status}</Badge></div>
      <ol aria-label={`Workflow timeline ${workflow.id}`} className="mt-4 grid gap-2 md:grid-cols-3">{workflow.events.map((event) => <li key={`${event.at}-${event.step}`} className="rounded-lg border border-white/[.08] bg-slate-950/35 p-3"><p className="text-[10px] font-semibold uppercase tracking-wider text-cyan-300">{event.step}</p><p className="mt-1 text-xs text-slate-400">{event.detail}</p></li>)}</ol>
      <div className="mt-4"><Button variant="secondary" disabled={busy} onClick={() => loadReplay(workflow.id)}>Replay verified history</Button></div>
      {replay?.workflow_id === workflow.id ? <WorkflowReplayPanel replay={replay} cursor={replayCursor} onCursor={setReplayCursor} /> : null}
    </Card>)}
    <Card className="p-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <label className="min-w-72 text-xs text-slate-300">Fixed isolated test profile<select aria-label="Isolated test profile" value={testProfileId} onChange={(event) => setTestProfileId(event.target.value)} className="mt-2 w-full rounded-lg border border-white/15 bg-slate-950 p-3 text-sm">{testProfiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.title}</option>)}</select></label>
        <Button variant="secondary" disabled={busy} onClick={refreshTestRuns}>Refresh workflow and test evidence</Button>
      </div>
      {testProfiles.find((profile) => profile.id === testProfileId) ? <div className="mt-4 rounded-lg border border-white/[.08] bg-slate-950/35 p-4 text-xs text-slate-400"><p>{testProfiles.find((profile) => profile.id === testProfileId)?.description}</p><p className="mt-2 font-mono text-[10px] text-cyan-300">network none · read-only candidate · {testProfiles.find((profile) => profile.id === testProfileId)?.memory_mb} MiB · {testProfiles.find((profile) => profile.id === testProfileId)?.timeout_seconds}s</p></div> : null}
    </Card>
    {testRuns.map((run) => {
      const profile = testProfiles.find((item) => item.id === run.profile_id);
      const failed = ["failed", "timed_out", "output_limit", "worker_failed", "interrupted"].includes(run.status);
      return <Card key={run.id} className="p-5">
        <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.16em] text-cyan-300">Isolated test evidence · attempt {run.attempt}</p><h3 className="mt-1 font-semibold">{profile?.title ?? run.profile_id}</h3><p className="mt-1 font-mono text-[10px] text-slate-500">digest {run.run_digest.slice(0, 16)}… · proposal {run.proposal_id.slice(0, 8)}{run.retry_of_id ? ` · retry of ${run.retry_of_id.slice(0, 8)}` : ""}</p></div><Badge tone={run.status === "passed" ? "success" : failed ? "danger" : "warning"}>{run.status}</Badge></div>
        {profile ? <pre aria-label={`Fixed test command ${run.id}`} className="mt-3 overflow-auto rounded-lg border border-white/[.08] bg-slate-950 p-3 text-[10px] text-slate-400"><code>{profile.command.join(" ")}</code></pre> : null}
        {run.output_excerpt ? <pre aria-label={`Test output ${run.id}`} className="mt-3 max-h-64 overflow-auto whitespace-pre-wrap rounded-lg border border-white/[.08] bg-slate-950 p-3 text-[11px] text-slate-300"><code>{run.output_excerpt}</code></pre> : null}
        <div className="mt-4 flex flex-wrap gap-2">{run.status === "pending_approval" ? <Button disabled={busy} onClick={() => transitionTest(run, "approve")}>Approve isolated test only</Button> : null}{["pending_approval", "queued", "running"].includes(run.status) ? <Button variant="secondary" disabled={busy} onClick={() => transitionTest(run, "cancel")}>Cancel test run</Button> : null}{run.status === "interrupted" ? <Button disabled={busy} onClick={() => retryTest(run)}>Create fresh retry approval</Button> : null}</div>
      </Card>;
    })}
    {proposals.map((proposal) => <Card key={proposal.id} className="p-5">
      <div className="flex flex-wrap items-start justify-between gap-3"><div><h3 className="font-semibold">{proposal.summary}</h3><p className="mt-1 font-mono text-[10px] text-slate-500">{proposal.path} · digest {proposal.proposal_digest.slice(0, 16)}…</p></div><Badge tone={proposal.status === "applied" ? "success" : proposal.status.includes("conflict") || proposal.status.includes("failed") ? "danger" : "warning"}>{proposal.status}</Badge></div>
      <p className="mt-3 text-xs text-slate-400">{proposal.rationale}</p>
      <pre aria-label={`Patch diff ${proposal.id}`} className="mt-4 max-h-80 overflow-auto whitespace-pre-wrap rounded-lg border border-white/[.08] bg-slate-950 p-4 text-[11px] leading-5 text-slate-300"><code>{proposal.unified_diff}</code></pre>
      <div className="mt-4 flex flex-wrap gap-2">{proposal.status === "pending" ? <Button disabled={busy} onClick={() => requestTests(proposal)}>Request isolated tests</Button> : null}{proposal.status === "pending" ? <Button variant="secondary" disabled={busy} onClick={() => transition(proposal, "approve")}>Approve and apply exact patch</Button> : null}{proposal.status === "applied" ? <Button variant="secondary" disabled={busy} onClick={() => transition(proposal, "rollback")}>Roll back exact patch</Button> : null}</div>
    </Card>)}
  </section>;
}
