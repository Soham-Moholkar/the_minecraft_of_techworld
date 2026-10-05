import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
import { POST } from "./events/route";

afterEach(() => vi.unstubAllGlobals());
it("rejects cross-origin writes before contacting the API", async () => {
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  const response = await POST(new Request("http://localhost:3000/api/streaming/usage/events", { method: "POST", headers: { Origin: "https://evil.example", "Content-Type": "application/json" }, body: '{"events":[]}' }));
  expect(response.status).toBe(403); expect(fetch).not.toHaveBeenCalled();
});
it("rejects caller-supplied tenant and redacts upstream errors", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('{"detail":"broker password secret"}', { status: 503 }));
  vi.stubGlobal("fetch", fetch);
  const bad = await POST(new Request("http://localhost:3000/api/streaming/usage/events", { method: "POST", headers: { Origin: "http://localhost:3000", "Content-Type": "application/json" }, body: '{"tenant":"other","events":[{"event_id":"one","units":4}]}' }));
  expect(bad.status).toBe(400); expect(fetch).not.toHaveBeenCalled();
  const result = await GET(); expect(result.status).toBe(503);
  expect(await result.text()).not.toContain("password");
  expect(result.headers.get("Cache-Control")).toBe("no-store");
});

it("cancels oversized streamed input before API forwarding", async () => {
  const fetcher = vi.fn(); vi.stubGlobal("fetch", fetcher);
  let cancelled = false;
  const body = new ReadableStream({ start(controller) { controller.enqueue(new TextEncoder().encode(" ".repeat(16001))); }, cancel() { cancelled = true; } });
  const options = { method: "POST", headers: { Origin: "http://localhost:3000" }, body, duplex: "half" } as RequestInit & { duplex: "half" };
  const response = await POST(new Request("http://localhost:3000/api/streaming/usage/events", options));
  expect(response.status).toBe(413); expect(cancelled).toBe(true);
  expect(fetcher).not.toHaveBeenCalled();
});

it("bounds streamed provider bytes and disallows redirects with server credentials", async () => {
  let cancelled = false;
  const body = new ReadableStream({ start(controller) { controller.enqueue(new Uint8Array(1000001)); }, cancel() { cancelled = true; } });
  const fetcher = vi.fn().mockResolvedValue(new Response(body)); vi.stubGlobal("fetch", fetcher);
  const response = await GET();
  expect(response.status).toBe(503); expect(cancelled).toBe(true);
  expect(fetcher.mock.calls[0][1].redirect).toBe("error");
  expect(await response.text()).not.toContain("password");
});
