import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { LockActivityViewer } from "./lock-activity-viewer";

const postgresActivity = {
  engine: "postgresql",
  available: true,
  total_locks: 7,
  waiting_locks: 2,
  buckets: [
    { mode: "AccessShareLock", granted: true, count: 5 },
    { mode: "RowExclusiveLock", granted: false, count: 2 },
  ],
  notes: ["Counts are an instantaneous database-wide aggregate, not a historical trace."],
  generated_at: "2026-08-28T09:30:00Z",
} as const;

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("LockActivityViewer", () => {
  it("renders granted and waiting aggregate buckets without sensitive identifiers", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify(postgresActivity), { status: 200, headers: { "Content-Type": "application/json" } }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<LockActivityViewer />);

    expect(screen.getByRole("status", { name: /loading lock activity/i })).toBeInTheDocument();
    expect(await screen.findByRole("table")).toHaveAccessibleName(/active postgresql database/i);
    expect(screen.getByText("AccessShareLock")).toBeInTheDocument();
    expect(screen.getByText("RowExclusiveLock")).toBeInTheDocument();
    expect(screen.getByText("Waiting")).toBeInTheDocument();
    expect(screen.getByText(/query text, process ids/i)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/database/lock-activity",
      expect.objectContaining({ cache: "no-store", signal: expect.any(AbortSignal) }),
    );

    fireEvent.click(screen.getByRole("button", { name: /reload snapshot/i }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  });

  it("explains provider unavailability instead of pretending there are no locks", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            ...postgresActivity,
            engine: "sqlite",
            available: false,
            total_locks: 0,
            waiting_locks: 0,
            buckets: [],
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    render(<LockActivityViewer />);

    expect(await screen.findByText(/live lock catalog unavailable/i)).toBeInTheDocument();
    expect(screen.getByText(/explicit provider limitation/i)).toBeInTheDocument();
  });

  it("fails closed when aggregate counts violate the runtime contract", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ ...postgresActivity, waiting_locks: -1 }), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    render(<LockActivityViewer />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/lock activity unavailable/i);
    expect(screen.getByRole("button", { name: /try again/i })).toBeEnabled();
  });
});
