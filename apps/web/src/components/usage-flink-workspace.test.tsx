import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { UsageFlinkWorkspace } from "./usage-flink-workspace";
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it("shows checkpoint counts and keeps missing pressure unavailable after refresh", async () => {
  const data = { provider: "flink", job_id: "a".repeat(32), state: "RUNNING", checkpoints: { completed: 2, failed: 1, in_progress: 0 }, vertices: [{ vertex_id: "b".repeat(32), level: null }], checked_at: "2026-10-04T00:00:00Z" };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(data))).mockResolvedValueOnce(new Response("{}", { status: 503 })));
  render(<UsageFlinkWorkspace/>);
  expect(await screen.findByText("Job state: RUNNING")).toBeVisible();
  expect(screen.getByText(/No current pressure sample/)).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Refresh Flink observation" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("unconfigured");
  expect(screen.queryByText("Job state: RUNNING")).not.toBeInTheDocument();
});
