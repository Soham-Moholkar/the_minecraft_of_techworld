import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DatabaseOperationsWorkbench } from "./database-operations-workbench";

const cacheProfile = {
  engine: "redis",
  status: "available",
  cache_state: "hit",
  project_total: 3,
  status_counts: [{ status: "active", count: 3 }],
  ttl_seconds: 24,
  consistency_model: "SQL authoritative; Redis cache-aside entries expire after 30 seconds.",
  notes: ["Cache failures fall back to SQL."],
  generated_at: "2026-09-01T12:00:00Z",
} as const;

const workbench = {
  engine: "sqlite",
  query_name: "tenant_projects_by_status",
  parameters: { query_name: "tenant_projects_by_status", status: "active", limit: 10 },
  items: [{ project_slug: "northstar-api", status: "active", note_count: 2, created_at: "2026-09-01T12:00:00Z" }],
  returned_count: 1,
  safety_model: "Named template with tenant predicate and row ceiling.",
  generated_at: "2026-09-01T12:00:00Z",
} as const;

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("DatabaseOperationsWorkbench", () => {
  it("renders cache evidence and runs only the named bounded query", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(cacheProfile), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(workbench), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DatabaseOperationsWorkbench />);

    await screen.findByText("Redis available");
    fireEvent.change(screen.getByLabelText(/row limit/i), { target: { value: "5" } });
    fireEvent.click(screen.getByRole("button", { name: /run query/i }));

    expect(await screen.findByText("northstar-api")).toBeInTheDocument();
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(JSON.parse(fetchMock.mock.calls[1][1].body as string)).toEqual({
      query_name: "tenant_projects_by_status",
      status: "active",
      limit: 5,
    });
    expect(screen.queryByRole("textbox", { name: /sql/i })).not.toBeInTheDocument();
  });

  it("shows independent cache and query failure states", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "cache offline" }), { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "query unavailable" }), { status: 503 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DatabaseOperationsWorkbench />);

    expect(await screen.findByRole("alert")).toHaveTextContent("cache offline");
    fireEvent.click(screen.getByRole("button", { name: /run query/i }));
    expect(await screen.findByText("query unavailable")).toBeInTheDocument();
  });
});
