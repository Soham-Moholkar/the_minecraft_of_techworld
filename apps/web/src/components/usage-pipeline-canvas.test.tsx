import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { UsagePipelineCanvas } from "./usage-pipeline-canvas";

const stream = { provider: "sqlite", topic: "atlas.usage.northstar", consumer: "usage-rollup", partitions: [{ partition: 0, earliest: 0, end: 4, checkpoint: 2, lag: 2, retention_gap: true }], units: 7, accepted: 2, quarantined: 1, processed: 0, delivery: "at-least-once" };
const compute = { checked_at: "2026-10-04T00:00:00Z", source_current: false, receipt: { schema_version: 1, provider: "spark", version: "4.2.0", tenant: "northstar", source_provider: "sqlite", source_digest: "a".repeat(64), rows: 1, units: 4, mode: "local", partitions: 1, duration_ms: 100, finished_at: "2026-10-03T00:00:00Z" } };
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it("selects actual lag/retention and stale lineage without implying branch runtime health", async () => {
  const fetcher = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(stream))).mockResolvedValueOnce(new Response(JSON.stringify(compute)));
  vi.stubGlobal("fetch", fetcher);
  render(<UsagePipelineCanvas/>);
  expect(await screen.findByText("2 accepted events · 7 usage units · 1 quarantined")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: /Usage topic/ }));
  expect(screen.getByText("Consumer lag: 2 · Retention gap: processing blocked")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: /Spark rollup/ }));
  expect(screen.getByText("Receipt belongs to an older source")).toBeVisible();
  expect(screen.getByText(`Export SHA-256: ${"a".repeat(64)}`)).toBeVisible();
  expect(screen.getByRole("button", { name: /Spark rollup/ })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: /Iceberg snapshots/ })).toHaveTextContent("Source-defined branch");
  for (const [path, options] of fetcher.mock.calls) {
    expect(["/api/streaming/usage", "/api/pipelines/usage/compute"]).toContain(path);
    expect(options.method).toBeUndefined();
    expect(options.cache).toBe("no-store");
  }
});

it("keeps valid streaming evidence when compute fails contract validation", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(stream))).mockResolvedValueOnce(new Response(JSON.stringify({ ...compute, checked_at: "invalid" }))));
  render(<UsagePipelineCanvas/>);
  expect(await screen.findByText("2 accepted events · 7 usage units · 1 quarantined")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: /Spark rollup/ }));
  expect(await screen.findByText("Compute evidence unavailable or disabled.")).toBeVisible();
  expect(screen.queryByText(/Export SHA-256:/)).not.toBeInTheDocument();
});

it("clears previous observations on refresh and preserves absence when providers fail", async () => {
  const fetcher = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(stream))).mockResolvedValueOnce(new Response(JSON.stringify(compute))).mockResolvedValue(new Response("{}", { status: 403 }));
  vi.stubGlobal("fetch", fetcher);
  render(<UsagePipelineCanvas/>);
  expect(await screen.findByText("2 accepted events · 7 usage units · 1 quarantined")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Refresh canvas evidence" }));
  expect(await screen.findByText("Streaming evidence unavailable or disabled.")).toBeVisible();
  expect(within(screen.getByRole("region", { name: "Selected pipeline stage" })).queryByText(/7 usage units/)).not.toBeInTheDocument();
});

it("aborts both independent reads on unmount", () => {
  const signals: AbortSignal[] = [];
  vi.stubGlobal("fetch", vi.fn((_path: string, options: RequestInit) => { signals.push(options.signal as AbortSignal); return new Promise(() => {}); }));
  const view = render(<UsagePipelineCanvas/>);
  expect(signals).toHaveLength(2);
  view.unmount();
  expect(signals.every(signal => signal.aborted)).toBe(true);
});
