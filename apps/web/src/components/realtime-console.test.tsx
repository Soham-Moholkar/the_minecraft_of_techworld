import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RealtimeConsole } from "./realtime-console";

const REQUEST_ID = "6b533e4d-2cc6-49af-a24a-033d80691027";

class FakeWebSocket {
  static readonly OPEN = 1;
  static readonly CLOSED = 3;
  static sent: string[] = [];

  readyState = 0;
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent<string>) => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;

  constructor(readonly url: string) {
    queueMicrotask(() => {
      this.readyState = FakeWebSocket.OPEN;
      this.onopen?.();
    });
  }

  send(payload: string) {
    FakeWebSocket.sent.push(payload);
    const request = JSON.parse(payload) as { request_id: string };
    queueMicrotask(() => {
      this.onmessage?.(
        new MessageEvent("message", {
          data: JSON.stringify({
            type: "presence.pong",
            request_id: request.request_id,
            organization_slug: "northstar",
            subject: "local-developer",
            server_time: "2026-08-27T17:30:00Z",
          }),
        }),
      );
    });
  }

  close(code = 1000) {
    this.readyState = FakeWebSocket.CLOSED;
    this.onclose?.(new CloseEvent("close", { code }));
  }
}

afterEach(() => {
  FakeWebSocket.sent = [];
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("RealtimeConsole", () => {
  it("exchanges a one-use ticket and renders an authenticated round trip", async () => {
    vi.stubGlobal("WebSocket", FakeWebSocket);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            url: "ws://localhost:8000/v1/realtime/ws?ticket=test-ticket-value-long-enough-12345",
            expires_in_seconds: 30,
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );
    vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue(REQUEST_ID);

    render(<RealtimeConsole />);

    expect(screen.getByRole("button", { name: /measure round trip/i })).toBeDisabled();
    await screen.findByText("northstar · local-developer");
    expect(screen.getByText("live")).toBeInTheDocument();
    expect(FakeWebSocket.sent).toHaveLength(1);

    fireEvent.click(screen.getByRole("button", { name: /measure round trip/i }));
    await waitFor(() => expect(FakeWebSocket.sent).toHaveLength(2));
    expect(fetch).toHaveBeenCalledWith(
      "/api/realtime/ticket",
      expect.objectContaining({ method: "POST", cache: "no-store" }),
    );
  });
});
