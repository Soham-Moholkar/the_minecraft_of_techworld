import { afterEach, expect, it, vi } from "vitest";
import { POST } from "./route";
const id = "11111111-1111-4111-8111-111111111111";
function request(origin = "http://localhost:3000") { return new Request("http://localhost:3000/api/ai/repository/patches/" + id + "/test-runs", { method: "POST", headers: { Origin: origin }, body: '{"profile_id":"api-agent-boundary"}' }); }
afterEach(() => vi.unstubAllGlobals());
it("uses the normalized id parameter and preserves redacted tool-disabled failures", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response('{"detail":"private"}', { status: 503 })); vi.stubGlobal("fetch", fetch);
  const result = await POST(request(), { params: Promise.resolve({ id }) });
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining(`/patches/${id}/test-runs`), expect.objectContaining({ method: "POST" }));
  expect(result.status).toBe(503); expect(await result.text()).not.toContain("private");
});
it("rejects cross-origin and malformed identifiers before delegating credentials", async () => {
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  expect((await POST(request("https://evil.example"), { params: Promise.resolve({ id }) })).status).toBe(403);
  expect((await POST(request(), { params: Promise.resolve({ id: "invalid" }) })).status).toBe(400);
  expect(fetch).not.toHaveBeenCalled();
});
