import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
afterEach(() => vi.unstubAllGlobals());
it("uses the fixed read-only endpoint and redacts failures", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('{"detail":"private file"}', { status: 503 })); vi.stubGlobal("fetch", fetch);
  const response = await GET();
  expect(response.status).toBe(503); expect(await response.text()).not.toContain("private file");
  expect(response.headers.get("cache-control")).toBe("no-store");
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/v1/infrastructure/deployment"), expect.objectContaining({ method: "GET", redirect: "error", cache: "no-store" }));
});
it("rejects malformed deployment observations", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response('{"status":"healthy","token":"private"}')));
  const response = await GET(); expect(response.status).toBe(502); expect(await response.text()).not.toContain("private");
});
