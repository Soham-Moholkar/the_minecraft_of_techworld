import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { IsolationVisualizer } from "./isolation-visualizer";

const baseProfile = {
  engine: "postgresql",
  current_isolation: "read_committed",
  default_isolation: "read_committed",
  capabilities: [
    {
      level: "read_committed",
      support: "native",
      effective_level: "read_committed",
      detail: "Each statement sees a snapshot taken when that statement begins.",
    },
    {
      level: "read_uncommitted",
      support: "mapped",
      effective_level: "read_committed",
      detail: "PostgreSQL maps this request to read committed.",
    },
  ],
  notes: ["Use explicit row locks when an invariant spans multiple statements."],
  generated_at: "2026-08-28T09:30:00Z",
} as const;

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("IsolationVisualizer", () => {
  it("renders active provider settings and the normalized isolation matrix", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(baseProfile), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<IsolationVisualizer />);

    expect(screen.getByRole("status", { name: /loading concurrency profile/i })).toBeInTheDocument();
    expect(await screen.findByRole("table")).toHaveAccessibleName(/active postgresql database provider/i);
    expect(screen.getByText("postgresql")).toBeInTheDocument();
    expect(screen.getAllByText("read committed").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("native")).toBeInTheDocument();
    expect(screen.getByText("mapped")).toBeInTheDocument();
    expect(screen.getByText(/maps this request to read committed/i)).toBeInTheDocument();
    expect(screen.getByText(/use explicit row locks/i)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/database/concurrency-profile",
      expect.objectContaining({ cache: "no-store", signal: expect.any(AbortSignal) }),
    );

    fireEvent.click(screen.getByRole("button", { name: /reload profile/i }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  });

  it("shows an actionable error when the response violates the runtime contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ ...baseProfile, engine: "unknown" }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    render(<IsolationVisualizer />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/concurrency profile unavailable/i);
    expect(screen.getByRole("button", { name: /try again/i })).toBeEnabled();
  });

  it("renders a dedicated empty state when the provider publishes no isolation ladder", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ ...baseProfile, capabilities: [] }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    render(<IsolationVisualizer />);

    expect(await screen.findByText(/no isolation levels reported/i)).toBeInTheDocument();
    expect(screen.getByText(/provider is reachable/i)).toHaveTextContent("postgresql");
  });
});
