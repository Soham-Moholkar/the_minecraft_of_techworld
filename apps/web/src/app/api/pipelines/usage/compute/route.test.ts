import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
afterEach(() => vi.unstubAllGlobals());
it("projects the fixed compute endpoint and rejects redirect/provider failures", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('{"detail":"private path"}', { status: 503 })); vi.stubGlobal("fetch", fetch);
  const response = await GET(); expect(response.status).toBe(503); expect(await response.text()).not.toContain("private path");
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/v1/pipelines/usage/compute"), expect.objectContaining({ method: "GET", cache: "no-store", redirect: "error" }));
});
