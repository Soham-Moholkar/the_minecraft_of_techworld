import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
afterEach(() => vi.unstubAllGlobals());
it("redacts credential failures for the fixed BI read", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('{"detail":"Bearer private"}', { status: 503 })); vi.stubGlobal("fetch", fetch);
  const response = await GET(); expect(response.status).toBe(503); expect(await response.text()).not.toContain("private");
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/v1/pipelines/usage/bi"), expect.objectContaining({ method: "GET", redirect: "error" }));
});
