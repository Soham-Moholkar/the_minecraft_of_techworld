import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
afterEach(() => vi.unstubAllGlobals());
it("keeps status read-only and redacts provider failures", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('{"detail":"Bearer private-value"}', { status: 503 })); vi.stubGlobal("fetch", fetch);
  const response = await GET(); expect(response.status).toBe(503); expect(await response.text()).not.toContain("private-value");
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/v1/pipelines/usage"), expect.objectContaining({ method: "GET", cache: "no-store" }));
});
