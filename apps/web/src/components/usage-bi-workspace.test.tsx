import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { UsageBiWorkspace } from "./usage-bi-workspace";
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it("distinguishes unpublished metadata and clears it on failure", async () => {
  const value = { provider: "superset", dashboard_id: 7, title: "ATLAS usage northstar", published: false, checked_at: "2026-10-04T00:00:00Z" };
  vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(value))).mockResolvedValueOnce(new Response("{}", { status: 503 })));
  render(<UsageBiWorkspace/>);
  expect(await screen.findByText("Dashboard unpublished")).toBeVisible();
  fireEvent.click(screen.getByRole("button", { name: "Refresh BI observation" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("unconfigured");
  expect(screen.queryByText("ATLAS usage northstar")).not.toBeInTheDocument();
});
