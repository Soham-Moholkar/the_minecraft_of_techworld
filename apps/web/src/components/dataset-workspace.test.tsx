import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DatasetWorkspace } from "./dataset-workspace";

const dataset = {
  id: "82744b4c-a496-4a9f-a9c3-e47445d7f6b0", name: "Service usage sample",
  source_checksum: "a".repeat(64), created_at: "2026-09-14T00:00:00Z", valid_rows: 2,
  profile: { input_rows: 4, valid_rows: 2, invalid_rows: 1, duplicate_rows: 1,
    service_count: 1, cost_total: 40, cost_mean: 20, cost_median: 20, cost_p95: 29,
    cost_stddev: 14, mean_ci95: [-107, 147], histogram: [{ lower: 10, upper: 30, count: 2 }],
    services: [{ service: "api", cost: 40, requests: 300 }],
    engines: ["pandas", "polars", "duckdb"].map((engine) => ({ engine, version: "1.0",
      p50_ms: 1, p95_ms: 2, repetitions: 3, matches_reference: true })),
    caveats: ["Measured locally."], generated_at: "2026-09-14T00:00:00Z" },
};
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("DatasetWorkspace", () => {
  it("imports a CSV and displays measured quality, histogram and engine evidence", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response("[]"))
      .mockResolvedValueOnce(new Response(JSON.stringify(dataset), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DatasetWorkspace />);
    await screen.findByText(/No datasets yet/);
    fireEvent.click(screen.getByRole("button", { name: "Load sample CSV" }));
    fireEvent.click(screen.getByRole("button", { name: "Import dataset" }));
    expect(await screen.findByRole("region", { name: "Dataset profile" })).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Cost histogram/ })).toBeInTheDocument();
    expect(screen.getAllByText("Matched")).toHaveLength(3);
    const request = JSON.parse(fetchMock.mock.calls[1][1].body as string);
    expect(request.csv_text).toContain("date,service,cost,requests");
    expect(request).not.toHaveProperty("organization_slug");
  });

  it("loads saved evidence and exposes a recoverable import failure", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([dataset])))
      .mockResolvedValueOnce(new Response(JSON.stringify(dataset)))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Invalid CSV" }), { status: 422 })));
    render(<DatasetWorkspace />);
    fireEvent.click(await screen.findByRole("button", { name: /Service usage sample/ }));
    expect(await screen.findByRole("region", { name: "Dataset profile" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Load sample CSV" }));
    fireEvent.click(screen.getByRole("button", { name: "Import dataset" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid CSV");
    expect(screen.getByRole("button", { name: "Import dataset" })).toBeEnabled();
  });
});
