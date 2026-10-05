import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
afterEach(() => vi.unstubAllGlobals());
it("fails closed on invalid Flink observations", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response('{"job_id":"../private","state":"ok"}')));
  const response = await GET(); expect(response.status).toBe(502); expect(response.headers.get("cache-control")).toBe("no-store");
  expect(await response.text()).not.toContain("private");
});
