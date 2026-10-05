import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { UsageComputeWorkspace } from "./usage-compute-workspace";
const data = { checked_at: "2026-10-03T00:00:00Z", source_current: false, receipt: { schema_version: 1, provider: "spark", version: "4.2.0", tenant: "northstar", source_provider: "sqlite", source_digest: "a".repeat(64), rows: 2, units: 7, mode: "standalone", partitions: 2, duration_ms: 100, finished_at: "2026-10-03T00:00:00Z" } };
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it("shows a stale observation without claiming current success", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(data))));
  render(<UsageComputeWorkspace/>);
  expect(await screen.findByText("Source has changed since this job")).toBeVisible();
  expect(screen.getByText("standalone")).toBeVisible();
  expect(screen.getByText("7")).toBeVisible();
});
it("distinguishes no receipt from disabled or failed providers", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ ...data, receipt: null, source_current: null }))).mockResolvedValueOnce(new Response("{}", { status: 503 })));
  render(<UsageComputeWorkspace/>);
  expect(await screen.findByText("No Spark receipt recorded for this tenant and provider.")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Refresh compute observation" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("unavailable or disabled");
  expect(screen.queryByText("No Spark receipt recorded for this tenant and provider.")).not.toBeInTheDocument();
});
