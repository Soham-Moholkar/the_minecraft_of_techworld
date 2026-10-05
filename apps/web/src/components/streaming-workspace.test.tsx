import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { StreamingWorkspace } from "./streaming-workspace";

const snapshot = { provider: "sqlite", topic: "atlas.usage.northstar", consumer: "usage-rollup",
  partitions: [{ partition: 0, earliest: 0, end: 1, checkpoint: 0, lag: 1, retention_gap: false }],
  units: 0, accepted: 0, quarantined: 0, processed: 0, delivery: "at-least-once" };
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

it("loads real lag and publishes an explicit event then processes a bounded batch", async () => {
  const fetch = vi.fn().mockImplementation(async () => new Response(JSON.stringify(snapshot)));
  vi.stubGlobal("fetch", fetch);
  render(<StreamingWorkspace/>);
  await screen.findByText("sqlite · atlas.usage.northstar · usage-rollup");
  fireEvent.change(screen.getByLabelText("Event ID"), { target: { value: "usage-one" } });
  fireEvent.change(screen.getByLabelText("Usage units"), { target: { value: "4" } });
  fireEvent.click(screen.getByRole("button", { name: "Publish event" }));
  await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/streaming/usage/events", expect.objectContaining({ body: JSON.stringify({ events: [{ event_id: "usage-one", units: 4 }] }) })));
  await waitFor(() => expect(screen.getByRole("button", { name: "Process up to 10 events" })).not.toBeDisabled());
  fireEvent.click(screen.getByRole("button", { name: "Process up to 10 events" }));
  await waitFor(() => expect(fetch).toHaveBeenCalledWith("/api/streaming/usage/consume", expect.objectContaining({ body: '{"limit":10}' })));
});

it("shows provider failure and allows refresh without enabling mutation", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: "Local streaming is disabled." }), { status: 403 })));
  render(<StreamingWorkspace/>);
  expect(await screen.findByRole("alert")).toHaveTextContent("Local streaming is disabled.");
  expect(screen.getByRole("button", { name: "Publish event" })).toBeDisabled();
  expect(screen.getByRole("button", { name: "Refresh" })).not.toBeDisabled();
});

it("publishes and displays bounded Iceberg snapshot history", async () => {
  const fetch = vi.fn().mockImplementation(async (url: string) => new Response(JSON.stringify(url.endsWith("/lakehouse")
    ? { provider: "iceberg-local", table: "northstar.usage_sqlite", snapshots: [{ snapshot_id: "9007199254740993", committed_at_ms: 100, operation: "append", rows: 1 }], rows: 1, units: 4, changed: true, source_digest: "a".repeat(64) }
    : snapshot)));
  vi.stubGlobal("fetch", fetch);
  render(<StreamingWorkspace/>);
  await screen.findByText("sqlite · atlas.usage.northstar · usage-rollup");
  fireEvent.click(screen.getByRole("button", { name: "Refresh local Iceberg snapshot" }));
  expect(await screen.findByRole("region", { name: "Lakehouse snapshot history" })).toHaveTextContent("9007199254740993");
  expect(fetch).toHaveBeenCalledWith("/api/streaming/usage/lakehouse", expect.objectContaining({ body: "{}", method: "POST" }));
});
