import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { UsageDagWorkspace } from "./usage-dag-workspace";
const data = { provider: "airflow", dag_id: "atlas_usage_rollup", checked_at: "2026-10-03T00:00:00Z", runs: [{ dag_run_id: "manual__reviewed", state: "failed", start_date: null, end_date: null }], latest_tasks: [{ task_id: "consume", state: "success", try_number: 1 }, { task_id: "validate_parquet", state: "failed", try_number: 2 }] };
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it("projects real runs and task attempts onto source-owned dependencies", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(data))));
  render(<UsageDagWorkspace/>);
  expect(await screen.findByText("manual__reviewed")).toBeVisible();
  expect(screen.getByText("success · attempt 1")).toBeVisible();
  expect(screen.getByText("failed · attempt 2")).toBeVisible();
  expect(screen.getByText("No current task observation")).toBeVisible();
});
it("clears old observations when a refresh fails", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(data))).mockResolvedValueOnce(new Response("{}", { status: 503 })));
  render(<UsageDagWorkspace/>);
  await screen.findByText("manual__reviewed");
  fireEvent.click(screen.getByRole("button", { name: "Refresh DAG status" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Airflow status unavailable");
  expect(screen.queryByText("manual__reviewed")).not.toBeInTheDocument();
});
it("distinguishes a real empty run list from an unavailable provider", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...data, runs: [], latest_tasks: [] }))));
  render(<UsageDagWorkspace/>);
  expect(await screen.findByText("No Airflow runs returned.")).toBeVisible();
  expect(screen.queryByRole("alert")).not.toBeInTheDocument();
});
