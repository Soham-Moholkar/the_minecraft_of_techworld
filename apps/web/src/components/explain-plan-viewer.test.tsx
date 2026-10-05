import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ExplainPlanViewer } from "./explain-plan-viewer";

const basePlan = {
  engine: "postgresql",
  query_name: "tenant_projects_by_status",
  parameters: { status: "active" },
  nodes: [
    {
      operation: "Index Scan",
      relation: "projects",
      detail: "Index Cond: ((organization_id = $1) AND (status = $2))",
      estimated_rows: 3,
      estimated_cost: 8.17,
    },
  ],
  recommendations: ["Keep tenant and status columns together for this access pattern."],
  generated_at: "2026-08-27T17:30:00Z",
} as const;

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("ExplainPlanViewer", () => {
  it("loads and renders normalized database evidence, then reloads on status change", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(basePlan), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<ExplainPlanViewer />);

    expect(screen.getByRole("status", { name: /loading query plan/i })).toBeInTheDocument();
    await screen.findByText("Index Scan");
    expect(screen.getByText("projects")).toBeInTheDocument();
    expect(screen.getByText(/keep tenant and status columns together/i)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/database/query-plan?status=active",
      expect.objectContaining({ cache: "no-store", signal: expect.any(AbortSignal) }),
    );

    fireEvent.change(screen.getByLabelText(/project status/i), { target: { value: "archived" } });
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(fetchMock).toHaveBeenLastCalledWith(
      "/api/database/query-plan?status=archived",
      expect.objectContaining({ cache: "no-store" }),
    );
  });

  it("shows an actionable error when the response violates the runtime contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ ...basePlan, engine: "unknown" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    render(<ExplainPlanViewer />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/plan unavailable/i);
    expect(screen.getByRole("button", { name: /try again/i })).toBeEnabled();
  });

  it("renders a dedicated empty state when a provider returns no operations", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ ...basePlan, nodes: [] }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    render(<ExplainPlanViewer />);

    expect(await screen.findByText(/no plan nodes returned/i)).toBeInTheDocument();
    expect(screen.getByText(/accepted the/i)).toHaveTextContent("active");
  });
});
