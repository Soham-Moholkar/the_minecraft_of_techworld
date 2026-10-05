import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { Dashboard } from "./dashboard";

const id = "11111111-1111-4111-8111-111111111111";
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it("shows authoritative project and audit evidence when health is unavailable", async () => {
  vi.stubGlobal("fetch", vi.fn(async (url: string) => url === "/api/health" ? new Response("{}", { status: 503 }) : new Response(JSON.stringify(url === "/api/projects" ? { items: [{ id, organization_id: id, slug: "real-project", name: "Persisted project", description: "Saved description", status: "paused", created_at: "2026-10-03T00:00:00Z" }], total: 7, limit: 25, offset: 0 } : [{ id, actor: "operator", action: "project.created", target_type: "project", target_id: id, details: {}, created_at: "2026-10-03T00:00:00Z" }]))));
  render(<Dashboard/>);
  expect(await screen.findByText("Persisted project")).toBeVisible();
  expect(await screen.findByText("project.created")).toBeVisible();
  expect(await screen.findByText("Unavailable")).toBeVisible();
  expect(screen.getByText("7")).toBeVisible();
  expect(screen.queryByText("99.96%")).not.toBeInTheDocument();
  expect(screen.queryByText("8.42M")).not.toBeInTheDocument();
});
it("keeps unavailable project data distinct from an empty inventory and aborts requests", async () => {
  const signals: AbortSignal[] = [];
  vi.stubGlobal("fetch", vi.fn(async (_url: string, options: RequestInit) => { signals.push(options.signal as AbortSignal); return new Response("{}", { status: 503 }); }));
  const view = render(<Dashboard/>);
  expect(await screen.findByText("Project inventory unavailable.")).toBeVisible();
  expect(screen.queryByText("No projects yet.")).not.toBeInTheDocument();
  view.unmount();
  expect(signals.every(signal => signal.aborted)).toBe(true);
});
