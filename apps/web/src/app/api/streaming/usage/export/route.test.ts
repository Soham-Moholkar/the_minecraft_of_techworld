import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
afterEach(() => vi.unstubAllGlobals());

it("preserves binary bytes and fixed download headers without redirects", async () => {
  const bytes = new Uint8Array([80, 65, 82, 49, 255, 0, 128]);
  const fetcher = vi.fn().mockResolvedValue(new Response(bytes, { headers: { "Content-Type": "application/vnd.apache.parquet", "Content-Disposition": "untrusted-filename" } }));
  vi.stubGlobal("fetch", fetcher);
  const response = await GET();
  expect(new Uint8Array(await response.arrayBuffer())).toEqual(bytes);
  expect(response.headers.get("Content-Disposition")).toBe('attachment; filename="atlas-usage.parquet"');
  expect(response.headers.get("X-Content-Type-Options")).toBe("nosniff");
  expect(response.headers.get("Cache-Control")).toBe("no-store");
  expect(fetcher.mock.calls[0][1].redirect).toBe("error");
});

it("cancels an oversized streaming download before unbounded allocation", async () => {
  let cancelled = false;
  const body = new ReadableStream({ start(controller) { controller.enqueue(new Uint8Array(2000001)); }, cancel() { cancelled = true; } });
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(body, { headers: { "Content-Type": "application/vnd.apache.parquet" } })));
  const response = await GET();
  expect(response.status).toBe(503);
  expect(cancelled).toBe(true);
});
