import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DatabaseProviderComparisonViewer } from "./database-provider-comparison";

const comparison = {
  providers: [
    { engine: "postgresql", role: "primary", status: "available", version: "18.0", current_isolation: "read_committed", default_isolation: "read_committed", query_plan_format: "json", transaction_model: "MVCC snapshots.", notes: ["Authoritative store."] },
    { engine: "mariadb", role: "comparison", status: "available", version: "12.3.2-MariaDB", current_isolation: "repeatable_read", default_isolation: "repeatable_read", query_plan_format: "json", transaction_model: "InnoDB MVCC.", notes: ["Observer account."] },
  ],
  generated_at: "2026-09-01T08:00:00Z",
} as const;

afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks(); });

describe("DatabaseProviderComparisonViewer", () => {
  it("renders live normalized providers and reloads", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(comparison), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DatabaseProviderComparisonViewer />);
    expect(screen.getByRole("status", { name: /loading database providers/i })).toBeInTheDocument();
    expect(await screen.findByText("12.3.2-MariaDB")).toBeInTheDocument();
    expect(screen.getAllByText("repeatable read")).toHaveLength(2);
    expect(screen.getByRole("link", { name: /open the mariadb lab/i })).toHaveAttribute("href", "/labs/database-mariadb-provider");
    fireEvent.click(screen.getByRole("button", { name: /reload providers/i }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  });

  it("rejects malformed upstream evidence", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...comparison, providers: [{ engine: "unknown" }] }), { status: 200 })));
    render(<DatabaseProviderComparisonViewer />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/provider comparison unavailable/i);
  });
});
