import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RepositoryPatchWorkspace } from "./repository-patch-workspace";

const file = {
  path: "apps/example.py", language: "Python", bytes: 10, lines: 1, sha256: "a".repeat(64),
};
const proposal = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  path: file.path,
  summary: "Replace the reviewed source range",
  rationale: "Apply a bounded change through exact-diff human approval.",
  status: "pending",
  original_sha256: file.sha256,
  patched_sha256: "b".repeat(64),
  proposal_digest: "c".repeat(64),
  unified_diff: "--- a/apps/example.py\n+++ b/apps/example.py\n-value = 1\n+value = 2\n",
  start_line: 1, end_line: 1, proposed_by: "local-developer", approved_by: null,
  failure_reason: null, created_at: "2026-09-23T10:00:00Z", approved_at: null,
  applied_at: null, rolled_back_at: null,
};
const workflow = {
  id: "6ba7b810-9dad-41d1-80b4-00c04fd430c8",
  objective: "Produce a validated patch proposal while preserving explicit human approval.",
  graph_version: 1,
  status: "awaiting_approval",
  current_step: "human_review",
  events: [
    { state: "submitted", step: "plan_received", at: "2026-09-23T10:00:00Z", detail: "Typed change plan accepted for deterministic validation." },
    { state: "validating", step: "policy_validation", at: "2026-09-23T10:00:01Z", detail: "Validating path, source hash, bounds, result syntax, and diff limits." },
    { state: "awaiting_approval", step: "human_review", at: "2026-09-23T10:00:02Z", detail: "Server-derived exact diff is waiting for explicit human approval." },
  ],
  failure_reason: null,
  created_by: "local-developer",
  created_at: "2026-09-23T10:00:00Z",
  updated_at: "2026-09-23T10:00:02Z",
  proposal,
};
const profile = {
  id: "api-agent-boundary", version: 1, title: "Agent boundary tests",
  description: "Patch, deterministic workflow, and isolated-run security tests.",
  command: ["python", "-m", "pytest", "tests/test_agent_tests.py", "-q"],
  cwd: "/workspace/apps/api-python", timeout_seconds: 180, memory_mb: 768,
  cpus: "1.0", pids_limit: 128, output_limit_bytes: 131072,
  network: "none", checkout: "staged-read-only",
};
const testRun = {
  id: "98b1d694-2e7b-46f5-9aab-731273f783ab",
  proposal_id: proposal.id, retry_of_id: null, attempt: 1,
  profile_id: profile.id, profile_version: 1,
  run_digest: "d".repeat(64), status: "pending_approval",
  requested_by: "local-developer", approved_by: null, output_excerpt: "",
  output_sha256: null, output_truncated: false, exit_code: null, duration_ms: null,
  failure_reason: null, cancel_requested: false, created_at: "2026-09-23T10:00:03Z",
  approved_at: null, started_at: null, finished_at: null,
};

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("RepositoryPatchWorkspace", () => {
  it("requires a visible exact diff before approval", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify([profile])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify(proposal), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        ...proposal, status: "applied", approved_by: "local-developer",
        approved_at: "2026-09-23T10:01:00Z", applied_at: "2026-09-23T10:01:01Z",
      })));
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryPatchWorkspace />);
    await screen.findByRole("option", { name: file.path });
    fireEvent.change(screen.getByRole("textbox", { name: "Patch replacement" }), {
      target: { value: "value = 2\n" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Create proposal directly" }));
    expect(await screen.findByLabelText(`Patch diff ${proposal.id}`)).toHaveTextContent("+value = 2");
    fireEvent.click(screen.getByRole("button", { name: "Approve and apply exact patch" }));
    expect(await screen.findByText("applied")).toBeInTheDocument();
    expect(JSON.parse(fetchMock.mock.calls[6][1].body as string)).toEqual({
      proposal_digest: proposal.proposal_digest,
      confirmation: "APPLY EXACT PATCH",
    });
  });

  it("renders the persisted deterministic state timeline before approval", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify([profile])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify(workflow), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryPatchWorkspace />);
    await screen.findByRole("option", { name: file.path });
    fireEvent.change(screen.getByRole("textbox", { name: "Patch replacement" }), {
      target: { value: "value = 2\n" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Run deterministic workflow" }));
    const timeline = await screen.findByRole("list", { name: `Workflow timeline ${workflow.id}` });
    expect(timeline).toHaveTextContent("plan_received");
    expect(timeline).toHaveTextContent("policy_validation");
    expect(timeline).toHaveTextContent("human_review");
    expect(await screen.findByLabelText(`Patch diff ${proposal.id}`)).toBeInTheDocument();
  });

  it("replays verified graph history one event at a time", async () => {
    const replay = {
      workflow_id: workflow.id,
      graph: {
        version: 1,
        nodes: [
          { state: "submitted", title: "Plan received", kind: "automatic", tool: null },
          { state: "awaiting_approval", title: "Human review", kind: "human_gate", tool: null },
        ],
        edges: [
          { source: "validating", target: "awaiting_approval", step: "human_review", condition: "proposal_ready", authority: "none" },
          { source: "awaiting_approval", target: "applied", step: "patch_applied", condition: "patch_approved", authority: "patch_approval" },
        ],
      },
      final_state: "awaiting_approval",
      frames: workflow.events.map((event, sequence) => ({
        sequence, kind: "transition", event,
        condition: sequence === 0 ? null : sequence === 1 ? "plan_accepted" : "proposal_ready",
        authority: "none",
      })),
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify([proposal])))
      .mockResolvedValueOnce(new Response(JSON.stringify([workflow])))
      .mockResolvedValueOnce(new Response(JSON.stringify([profile])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify(replay)));
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryPatchWorkspace />);
    fireEvent.click(await screen.findByRole("button", { name: "Replay verified history" }));
    const viewer = await screen.findByLabelText(`Workflow replay ${workflow.id}`);
    expect(viewer).toHaveTextContent("Policy graph v1");
    expect(viewer).toHaveTextContent("proposal_ready");
    expect(screen.getByRole("list", { name: "Available policy branches" })).toHaveTextContent("patch_approved → applied · patch_approval");
    fireEvent.click(screen.getByRole("button", { name: "Previous event" }));
    expect(viewer).toHaveTextContent("plan_accepted");
    expect(fetchMock.mock.calls[5][0]).toBe(`/api/ai/repository/workflows/${workflow.id}/replay`);
  });

  it("keeps isolated test approval separate from patch application", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify([proposal])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify([profile])))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify(testRun), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        ...testRun, status: "queued", approved_by: "local-developer",
        approved_at: "2026-09-23T10:01:00Z",
      })));
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryPatchWorkspace />);
    await screen.findByRole("option", { name: profile.title });
    fireEvent.click(screen.getByRole("button", { name: "Request isolated tests" }));
    expect(await screen.findByText("pending_approval")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Approve isolated test only" }));
    expect(await screen.findByText("queued")).toBeInTheDocument();
    expect(JSON.parse(fetchMock.mock.calls[6][1].body as string)).toEqual({
      run_digest: testRun.run_digest,
      confirmation: "RUN ISOLATED TEST PROFILE",
    });
    expect(screen.getByRole("button", { name: "Approve and apply exact patch" })).toBeInTheDocument();
  });

  it("creates fresh approval evidence when an interrupted run is retried", async () => {
    const interrupted = {
      ...testRun,
      status: "interrupted",
      failure_reason: "worker_heartbeat_expired",
      finished_at: "2026-09-23T10:05:00Z",
    };
    const retry = {
      ...testRun,
      id: "ca5df7a6-3194-4a57-aef5-b4d860fc49d5",
      retry_of_id: testRun.id,
      attempt: 2,
      run_digest: "e".repeat(64),
      created_at: "2026-09-23T10:06:00Z",
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify([proposal])))
      .mockResolvedValueOnce(new Response(JSON.stringify([workflow])))
      .mockResolvedValueOnce(new Response(JSON.stringify([profile])))
      .mockResolvedValueOnce(new Response(JSON.stringify([interrupted])))
      .mockResolvedValueOnce(new Response(JSON.stringify(retry), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryPatchWorkspace />);
    fireEvent.click(await screen.findByRole("button", { name: "Create fresh retry approval" }));
    expect(await screen.findByText("Isolated test evidence · attempt 2")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Approve isolated test only" })).toBeInTheDocument();
    const timeline = screen.getByRole("list", { name: `Workflow timeline ${workflow.id}` });
    expect(timeline).toHaveTextContent("test_retry_requested");
    expect(fetchMock.mock.calls[5][0]).toBe(`/api/ai/repository/test-runs/${testRun.id}/retry`);
  });
});
