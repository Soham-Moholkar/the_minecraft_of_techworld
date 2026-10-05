import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { MachineLearningWorkspace } from "./machine-learning-workspace";

const dataset = { id: "82744b4c-a496-4a9f-a9c3-e47445d7f6b0", name: "Service usage",
  source_checksum: "a".repeat(64), created_at: "2026-09-15T00:00:00Z", valid_rows: 60 };
const metrics = { accuracy: 0.8, balanced_accuracy: 0.8, precision: 0.8, recall: 0.8,
  f1: 0.8, roc_auc: 0.9, confusion_matrix: [[6, 1], [2, 6]] };
const experiment = {
  id: "a4994b4c-a496-4a9f-a9c3-e47445d7f6b1", dataset_id: dataset.id,
  dataset_name: dataset.name, name: "Service risk", created_at: "2026-09-15T00:00:00Z",
  best_model: "logistic_regression", best_balanced_accuracy: 0.8,
  report: { task: "high_cost_classification", target_definition: "cost greater than median",
    training_rows: 45, test_rows: 15, positive_rate: 0.5, random_seed: 42, sklearn_version: "1.9.1",
    models: ["logistic_regression", "decision_tree", "numpy_logistic"].map((model, index) => ({
      model, implementation: index === 2 ? "from-scratch" : "scikit-learn", fit_ms: 2, metrics,
    })), feature_effects: ["requests", "day", "service"].map((feature) => ({
      feature, importance_mean: 0.1, importance_stddev: 0.02,
    })), caveats: ["Holdout evidence is workload-specific."] },
};

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("MachineLearningWorkspace", () => {
  it("submits the neural suite and renders accessible loss evidence", async () => {
    const neural = structuredClone(experiment);
    const report = { ...neural.report, torch_version: "2.14.0+cpu", tensorflow_version: "2.21.0", keras_version: "3.15.1", models: [
      ...neural.report.models, { model: "pytorch_mlp", implementation: "pytorch", fit_ms: 50,
        metrics, training_curve: Array.from({ length: 80 }, (_, i) => ({ epoch: i + 1, loss: 1 / (i + 1) })) },
      { model: "keras_mlp", implementation: "tensorflow-keras", fit_ms: 100,
        metrics, training_curve: Array.from({ length: 80 }, (_, i) => ({ epoch: i + 1, loss: 1 / (i + 2) })) },
    ] };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([dataset])))
      .mockResolvedValueOnce(new Response("[]"))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ...neural, report }), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<MachineLearningWorkspace />);
    await screen.findByText(/No experiments yet/);
    fireEvent.change(screen.getByLabelText("Comparison suite"), { target: { value: "frameworks" } });
    fireEvent.click(screen.getByRole("button", { name: "Run experiment" }));
    expect(await screen.findAllByRole("img", { name: /Training loss from/ })).toHaveLength(2);
    expect(screen.getAllByText("Inspect epoch values")).toHaveLength(2);
    expect(JSON.parse(fetchMock.mock.calls[2][1].body as string).suite).toBe("frameworks");
  });
  it("trains and renders model, evaluation, and interpretation evidence", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([dataset])))
      .mockResolvedValueOnce(new Response("[]"))
      .mockResolvedValueOnce(new Response(JSON.stringify(experiment), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<MachineLearningWorkspace />);
    await screen.findByText(/No experiments yet/);
    fireEvent.click(screen.getByRole("button", { name: "Run experiment" }));
    expect(await screen.findByRole("region", { name: "Experiment report" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Permutation feature effects/ })).toBeInTheDocument();
    expect(screen.getByText("numpy logistic")).toBeInTheDocument();
    const request = JSON.parse(fetchMock.mock.calls[2][1].body as string);
    expect(request.dataset_id).toBe(dataset.id);
    expect(request).not.toHaveProperty("organization_id");
  });

  it("loads saved evidence and recovers from training failure", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([dataset])))
      .mockResolvedValueOnce(new Response(JSON.stringify([experiment])))
      .mockResolvedValueOnce(new Response(JSON.stringify(experiment)))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Dataset too small" }), { status: 422 })));
    render(<MachineLearningWorkspace />);
    fireEvent.click(await screen.findByRole("button", { name: /Service risk/ }));
    expect(await screen.findByRole("region", { name: "Experiment report" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Run experiment" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Dataset too small");
    expect(screen.getByRole("button", { name: "Run experiment" })).toBeEnabled();
  });
});
