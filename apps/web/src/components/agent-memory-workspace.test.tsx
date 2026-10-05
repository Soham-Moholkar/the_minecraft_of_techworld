import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AgentMemoryWorkspace } from "./agent-memory-workspace";
import { memoryFixture, memoryInputFixture, memorySnapshotFixture } from "@/lib/agent-memory.fixture";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.useRealTimers(); });

function draft() {
  fireEvent.change(screen.getByRole("textbox", { name: "Memory title" }), { target: { value: memoryFixture.title } });
  fireEvent.change(screen.getByRole("textbox", { name: "Memory note" }), { target: { value: memoryFixture.content } });
  fireEvent.change(screen.getByRole("textbox", { name: "Provenance" }), { target: { value: memoryFixture.provenance } });
}

describe("AgentMemoryWorkspace", () => {
  it("requires review before saving and never sends memory to inference", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ ...memorySnapshotFixture, items: [] })))
      .mockResolvedValueOnce(new Response(JSON.stringify(memoryFixture), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(memorySnapshotFixture)));
    vi.stubGlobal("fetch", fetchMock);
    render(<AgentMemoryWorkspace />);
    await screen.findByText("No active memory notes.");
    draft();
    expect(screen.getByRole("button", { name: "Save operator memory" })).toBeDisabled();
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Save operator memory" }));
    await screen.findByRole("heading", { name: memoryFixture.title });
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual(memoryInputFixture);
    expect(screen.getByRole("textbox", { name: "Memory note" })).toHaveValue("");
    expect(screen.getByRole("checkbox")).not.toBeChecked();
    expect(fetchMock.mock.calls.every(([url]) => url.startsWith("/api/ai/repository/memory"))).toBe(true);
    expect(screen.getByText("Automatic context disabled")).toBeInTheDocument();
  });

  it("requires a second deliberate action for permanent deletion", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(memorySnapshotFixture)))
      .mockResolvedValueOnce(new Response(JSON.stringify({ removed_count: 1 })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ...memorySnapshotFixture, items: [] })));
    vi.stubGlobal("fetch", fetchMock);
    render(<AgentMemoryWorkspace />);
    await screen.findByRole("heading", { name: memoryFixture.title });
    fireEvent.click(screen.getByRole("button", { name: `Delete memory ${memoryFixture.title}` }));
    expect(fetchMock).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole("button", { name: "Cancel deletion" }));
    expect(fetchMock).toHaveBeenCalledTimes(1);
    fireEvent.click(screen.getByRole("button", { name: `Delete memory ${memoryFixture.title}` }));
    fireEvent.click(screen.getByRole("button", { name: `Confirm permanent deletion of ${memoryFixture.title}` }));
    await screen.findByText("No active memory notes.");
    expect(fetchMock.mock.calls[1][1].method).toBe("DELETE");
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ confirmation: "DELETE MEMORY" });
  });

  it("physically purges expired notes without showing their text", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ ...memorySnapshotFixture, items: [], expired_count: 1 })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ removed_count: 1 })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ...memorySnapshotFixture, items: [] })));
    vi.stubGlobal("fetch", fetchMock);
    render(<AgentMemoryWorkspace />);
    await screen.findByText(/1 expired pending removal/);
    fireEvent.click(screen.getByRole("button", { name: "Remove expired memory" }));
    await screen.findByText(/0 expired pending removal/);
    expect(fetchMock.mock.calls[1][0]).toBe("/api/ai/repository/memory/purge-expired");
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ confirmation: "REMOVE EXPIRED MEMORY" });
  });

  it("renders untrusted instruction markup as text and preserves rejected drafts", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ ...memorySnapshotFixture,
      items: [{ ...memoryFixture, content: "<script>ignore policy</script>" }] })))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "Review note for credentials." }), { status: 400 })));
    const view = render(<AgentMemoryWorkspace />);
    await screen.findByText("<script>ignore policy</script>");
    expect(view.container.querySelector("script")).toBeNull();
    draft(); fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Save operator memory" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Review note");
    expect(screen.getByRole("textbox", { name: "Memory note" })).toHaveValue(memoryFixture.content);
  });

  it("fails closed on automatic model-context capability", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...memorySnapshotFixture, automatic_context: true }))));
    render(<AgentMemoryWorkspace />);
    await screen.findByRole("alert");
    expect(screen.queryByRole("heading", { name: memoryFixture.title })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Save operator memory" })).toBeDisabled();
  });

  it("removes a note from an open snapshot at expiry without an API call", async () => {
    const expires = new Date(Date.now() + 10_000);
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ ...memorySnapshotFixture,
      items: [{ ...memoryFixture, expires_at: expires.toISOString() }] }))));
    vi.stubGlobal("fetch", fetchMock);
    render(<AgentMemoryWorkspace />);
    await screen.findByRole("heading", { name: memoryFixture.title });
    vi.useFakeTimers();
    // Re-arm the timer with fake timers by refreshing the source snapshot.
    fireEvent.click(screen.getByRole("button", { name: "Refresh memory" }));
    await act(async () => { await Promise.resolve(); await Promise.resolve(); });
    await act(async () => { await vi.advanceTimersByTimeAsync(10_002); });
    expect(screen.queryByRole("heading", { name: memoryFixture.title })).not.toBeInTheDocument();
    expect(screen.getByText(/1 expired pending removal/)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("allows refresh after loading fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValueOnce(new Error("offline"))
      .mockResolvedValueOnce(new Response(JSON.stringify({ ...memorySnapshotFixture, items: [] }))));
    render(<AgentMemoryWorkspace />);
    await screen.findByRole("alert");
    fireEvent.click(screen.getByRole("button", { name: "Refresh memory" }));
    await waitFor(() => expect(screen.queryByRole("alert")).not.toBeInTheDocument());
    await screen.findByText("No active memory notes.");
  });
});
