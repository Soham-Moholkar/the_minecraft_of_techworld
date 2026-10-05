import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RepositoryAIWorkspace } from "./repository-ai-workspace";

const file = {
  path: "apps/api-python/src/atlas_api/repository_ai.py",
  language: "Python",
  bytes: 120,
  lines: 2,
  sha256: "a".repeat(64),
};
const explanation = {
  file,
  start_line: 1,
  end_line: 2,
  intent: "explain",
  provider: "openai",
  model: "gpt-5.6-luna",
  overview: "This module defines the bounded repository intelligence boundary.",
  architecture_relations: ["The HTTP route depends on this provider contract."],
  suggested_change: null,
  lines: [
    { line_number: 1, code: "from pathlib import Path", explanation: "Imports the path abstraction.", keywords: [{ token: "from", meaning: "selective import keyword" }], relations: [] },
    { line_number: 2, code: "", explanation: "Separates imports from declarations.", keywords: [], relations: [] },
  ],
  usage: { input_tokens: 120, output_tokens: 80, estimated_cost_usd: 0.00012 },
};
const providers = [
  { provider: "openai", configured: true, reachable: true, model: "gpt-5.6-luna", latency_ms: 80, detail: "ready" },
  { provider: "local", configured: false, reachable: false, model: "local-code-model", latency_ms: null, detail: "disabled" },
];
const operations = {
  budget: { monthly_limit_usd: 25, committed_usd: 0, reserved_usd: 0, remaining_usd: 25 },
  slo: {
    sample_count: 0,
    availability: null,
    p95_seconds: null,
    availability_target: 0.99,
    p95_seconds_target: 30,
    availability_met: null,
    latency_met: null,
  },
};
const streamedExplanation = () => new Response(
  `event: delta\ndata: ${JSON.stringify({ delta: '{"overview":' })}\n\n` +
  `event: result\ndata: ${JSON.stringify(explanation)}\n\n`,
  { headers: { "Content-Type": "text/event-stream" } },
);
const retrieval = {
  query: "provider stream structured validation",
  mode: "hybrid",
  embedding_provider: "hashing-v1",
  indexed_files: 12,
  indexed_chunks: 30,
  cache_hits: 10,
  cache_misses: 2,
  truncated: false,
  hits: [{
    citation: { id: "0123456789abcdef", path: file.path, start_line: 1, end_line: 2, sha256: file.sha256 },
    snippet: "from pathlib import Path\n",
    lexical_score: 0.75,
    embedding_score: 0.6,
    final_score: 0.693,
    prompt_injection_signals: [],
  }],
};
const evaluation = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  name: "Repository retrieval regression",
  report: {
    grounding_passed: true,
    citation_accuracy: 1,
    injection_detection_passed: true,
    cases: [{ id: "grounding", passed: true, hit_count: 6 }],
  },
  created_by: "owner",
  created_at: "2026-09-21T10:00:00Z",
};

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("RepositoryAIWorkspace", () => {
  it("keeps source and commentary in separate side-by-side cells", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify(providers)))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify(operations)))
      .mockResolvedValueOnce(streamedExplanation());
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryAIWorkspace />);
    await screen.findByRole("option", { name: file.path });
    fireEvent.change(screen.getByRole("spinbutton", { name: "End line" }), { target: { value: "2" } });
    fireEvent.click(screen.getByRole("button", { name: "Explain source" }));
    expect(await screen.findByRole("table", { name: "Code with side explanations" })).toBeInTheDocument();
    expect(screen.getByText("from pathlib import Path")).toBeInTheDocument();
    expect(screen.getByText("Imports the path abstraction.")).toBeInTheDocument();
    expect(screen.getByText("gpt-5.6-luna")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    expect(screen.getByText("disabled")).toBeInTheDocument();
    expect(fetchMock.mock.calls[4][0]).toBe("/api/ai/repository/stream");
    expect(JSON.parse(fetchMock.mock.calls[4][1].body as string)).toMatchObject({
      path: file.path,
      start_line: 1,
      end_line: 2,
      tier: "auto",
      provider: "auto",
    });
  });

  it("surfaces missing provider configuration without losing the catalog", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify(providers)))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify(operations)))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Repository AI is not configured." }), { status: 503 })));
    render(<RepositoryAIWorkspace />);
    await screen.findByRole("option", { name: file.path });
    fireEvent.change(screen.getByRole("spinbutton", { name: "End line" }), { target: { value: "2" } });
    fireEvent.click(screen.getByRole("button", { name: "Explain source" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Repository AI is not configured.");
  });

  it("shows exact retrieval citations and persisted evaluation evidence", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify(providers)))
      .mockResolvedValueOnce(new Response(JSON.stringify([])))
      .mockResolvedValueOnce(new Response(JSON.stringify(operations)))
      .mockResolvedValueOnce(new Response(JSON.stringify(retrieval)))
      .mockResolvedValueOnce(new Response(JSON.stringify(evaluation), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<RepositoryAIWorkspace />);
    await screen.findByRole("option", { name: file.path });

    fireEvent.click(screen.getByRole("button", { name: "Search repository" }));
    expect(await screen.findByRole("region", { name: "Repository retrieval results" })).toHaveTextContent(
      `${file.path}:1-2`,
    );
    expect(screen.getByText("Content scan clear")).toBeInTheDocument();
    expect(fetchMock.mock.calls[4][0]).toBe("/api/ai/repository/retrieval");

    fireEvent.click(screen.getByRole("button", { name: "Run regression evaluation" }));
    expect(await screen.findByRole("region", { name: "Retrieval evaluation" })).toHaveTextContent(
      "100% citations",
    );
    expect(fetchMock.mock.calls[5][0]).toBe("/api/ai/repository/retrieval/evaluations");
  });
});
