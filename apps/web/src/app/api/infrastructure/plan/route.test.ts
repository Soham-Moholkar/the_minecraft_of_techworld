import { afterEach, expect, it, vi } from "vitest";
import { GET } from "./route";
afterEach(() => vi.unstubAllGlobals());
it("uses only the fixed read endpoint and redacts provider values", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('{"secret":"private"}',{status:503})); vi.stubGlobal("fetch",fetch);
  const response = await GET(); expect(response.status).toBe(503); expect(await response.text()).not.toContain("private");
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/v1/infrastructure/plan"),expect.objectContaining({method:"GET",redirect:"error",cache:"no-store"}));
});
it("rejects contradictory missing-receipt lineage", async () => {
  vi.stubGlobal("fetch",vi.fn().mockResolvedValue(new Response(JSON.stringify({checked_at:"2026-10-04T00:00:00Z",source_current:true,receipt:null}))));
  expect((await GET()).status).toBe(502);
});
