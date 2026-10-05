import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AppliedAIWorkspace } from "./applied-ai-workspace";

const curve = Array.from({ length: 20 }, (_, index) => ({ epoch: index + 1, loss: 1 / (index + 1) }));
const tasks = [
  ["computer_vision", "accuracy", true], ["time_series", "mae", false],
  ["nlp_attention", "accuracy", true], ["recommendation", "hit_rate_at_3", true],
].map(([task, metric, higher]) => ({ task, architecture: "bounded model", baseline: "baseline",
  metric, higher_is_better: higher, model_score: higher ? 0.9 : 1,
  baseline_score: higher ? 0.5 : 4, training_curve: curve, train_examples: 100, test_examples: 20 }));
const experiment = { id: "a4994b4c-a496-4a9f-a9c3-e47445d7f6b9", name: "Applied suite",
  created_at: "2026-09-18T00:00:00Z", tasks: 4, improved_tasks: 4,
  report: { suite: "phase7_applied_ai", random_seed: 42, torch_version: "2.14.0+cpu",
    tasks, caveats: ["Fixed workload."] } };

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("AppliedAIWorkspace", () => {
  it("runs all task families and renders model, baseline, and loss evidence", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response("[]"))
      .mockResolvedValueOnce(new Response(JSON.stringify(experiment), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<AppliedAIWorkspace />);
    await screen.findByText("No applied runs yet.");
    fireEvent.click(screen.getByRole("button", { name: "Run applied suite" }));
    expect(await screen.findByRole("region", { name: "Applied AI report" })).toBeInTheDocument();
    expect(screen.getAllByRole("img", { name: /training loss/i })).toHaveLength(4);
    expect(screen.getByText("NLP + attention")).toBeInTheDocument();
    expect(JSON.parse(fetchMock.mock.calls[1][1].body as string)).toEqual({
      name: "Phase 7 applied AI compatibility",
    });
  });

  it("loads saved evidence and surfaces redacted service failures", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([experiment])))
      .mockResolvedValueOnce(new Response(JSON.stringify(experiment)))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Service unavailable." }), { status: 503 })));
    render(<AppliedAIWorkspace />);
    fireEvent.click(await screen.findByRole("button", { name: /Applied suite/ }));
    expect(await screen.findByText("Computer vision")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Run applied suite" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Service unavailable.");
  });
});
