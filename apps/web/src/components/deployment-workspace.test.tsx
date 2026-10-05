import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { DeploymentWorkspace } from "./deployment-workspace";
const data = { namespace: "atlas-dev", release: "atlas", checked_at: "2026-10-04T00:00:00Z", manifest_digest: "a".repeat(64), status: "passed", cluster_status: "not_checked", resources: [{ kind: "PersistentVolumeClaim", name: "atlas-data", retained: true, matches_contract: true }], findings: [], budget: { cpu_request_millicores: 350, cpu_limit_millicores: 2000, memory_request_mib: 768, memory_limit_mib: 1536, storage_mib: 1024, replicas: 2 }, teardown: ["kubectl --context kind-atlas --namespace atlas-dev delete deployment atlas-api"], retained: ["Namespace atlas-dev", "PersistentVolumeClaim atlas-data", "External Secret atlas-operator"] };
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it("separates offline policy from live health and exposes only a review plan", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify(data))); vi.stubGlobal("fetch", fetch);
  render(<DeploymentWorkspace/>);
  expect(screen.getByRole("status")).toHaveTextContent("Checking owned manifest");
  expect(await screen.findByText("Local checks passed")).toBeVisible();
  expect(screen.getByText("Not checked")).toBeVisible();
  expect(screen.getByText("350 / 2000 mCPU")).toBeVisible();
  expect(screen.getByText("External Secret atlas-operator")).toBeVisible();
  const button = screen.getByRole("button", { name: "Inspect teardown plan" });
  fireEvent.click(button);
  expect(screen.getByText("Review only. No command has been executed.")).toBeVisible();
  expect(button).toHaveAttribute("aria-expanded", "true");
  expect(fetch).toHaveBeenCalledTimes(1);
});
it("withholds unsafe budgets and disables teardown for policy findings", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...data, status: "blocked", budget: null, teardown: [], findings: [{ code: "resource-contract", message: "Review Deployment atlas-api against the owned policy." }] }))));
  render(<DeploymentWorkspace/>);
  expect(await screen.findByText("Deployment review blocked")).toBeVisible();
  expect(screen.getByRole("alert")).toHaveTextContent("Review Deployment");
  expect(screen.getByRole("button", { name: "Inspect teardown plan" })).toBeDisabled();
  expect(screen.queryByText("350 / 2000 mCPU")).not.toBeInTheDocument();
});
it("clears previous evidence on a failed refresh and cancels unmounted requests", async () => {
  const fetch = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(data))).mockResolvedValueOnce(new Response("{}", { status: 503 }));
  vi.stubGlobal("fetch", fetch);
  const view = render(<DeploymentWorkspace/>);
  await screen.findByText("Local checks passed");
  fireEvent.click(screen.getByRole("button", { name: "Refresh deployment review" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("unavailable or disabled");
  expect(screen.queryByText("Local checks passed")).not.toBeInTheDocument();
  view.unmount();
  expect(fetch.mock.calls[1][1].signal.aborted).toBe(true);
});
