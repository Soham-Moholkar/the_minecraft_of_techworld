import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DocumentProjectionViewer } from "./document-projection-viewer";

const readySnapshot = {
  engine: "mongodb",
  status: "available",
  document_count: 1,
  published_at: "2026-09-01T08:00:00Z",
  items: [{ project_slug: "atlas-core", status: "active", note_count: 3, created_at: "2026-08-27T08:00:00Z" }],
  index_strategy: "organization_slug + generation + created_at compound tenant index",
  consistency_model: "PostgreSQL authoritative; complete MongoDB generations switch atomically.",
  notes: ["Projection refresh is explicit."],
  generated_at: "2026-09-01T08:00:01Z",
} as const;

afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks(); });

describe("DocumentProjectionViewer", () => {
  it("renders an allowlisted snapshot and republishes it", async () => {
    const publishResult = { engine: "mongodb", published_count: 1, removed_count: 2, published_at: "2026-09-01T08:01:00Z" };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(readySnapshot), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(publishResult), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(readySnapshot), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    render(<DocumentProjectionViewer />);
    expect(screen.getByRole("status", { name: /loading mongodb projection/i })).toBeInTheDocument();
    expect(await screen.findByRole("rowheader", { name: "atlas-core" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open the mongodb lab/i })).toHaveAttribute("href", "/labs/database-mongodb-document-model");

    fireEvent.click(screen.getByRole("button", { name: /publish projection/i }));
    expect(await screen.findByRole("status")).toHaveTextContent(/published 1 documents; removed 2/i);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3));
    expect(fetchMock.mock.calls[1]?.[1]).toMatchObject({ method: "POST" });
  });

  it("explains an unavailable optional provider and disables publishing", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...readySnapshot, status: "unavailable", document_count: 0, published_at: null, items: [] }), { status: 200 })));
    render(<DocumentProjectionViewer />);
    expect(await screen.findByText(/start the optional mongodb compose profile/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /publish projection/i })).toBeDisabled();
  });

  it("fails closed on a malformed browser contract", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...readySnapshot, items: [{ project_slug: "x", secret: "must-not-render" }] }), { status: 200 })));
    render(<DocumentProjectionViewer />);
    expect(await screen.findByRole("alert")).toHaveTextContent(/projection request failed/i);
    expect(screen.queryByText("must-not-render")).not.toBeInTheDocument();
  });
});
