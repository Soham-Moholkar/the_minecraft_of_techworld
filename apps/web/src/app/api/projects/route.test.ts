import { afterEach, expect, it, vi } from "vitest";
import { GET, POST } from "./route";
import { POST as postNote } from "./[projectId]/notes/route";
const id = "11111111-1111-4111-8111-111111111111";
const payload = { organization_id: id, slug: "valid-project", name: "New project" };
function request(body: unknown, origin = "http://localhost:3000") { return new Request("http://localhost:3000/api/projects", { method: "POST", headers: { Origin: origin }, body: JSON.stringify(body) }); }
afterEach(() => { vi.unstubAllGlobals(); });
it("blocks cross-origin project and note writes without delegating credentials", async () => {
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  expect((await POST(request(payload, "https://evil.example"))).status).toBe(403);
  expect((await postNote(request({ author: "Owner", body: "note" }, "https://evil.example"), { params: Promise.resolve({ projectId: id }) })).status).toBe(403);
  expect(fetch).not.toHaveBeenCalled();
});
it("rejects invalid, unknown and oversized input before contacting the provider", async () => {
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  expect((await POST(request({ ...payload, command: "arbitrary" }))).status).toBe(400);
  expect((await POST(request({ ...payload, name: "" }))).status).toBe(400);
  expect((await POST(request({ ...payload, description: "x".repeat(16001) }))).status).toBe(413);
  expect((await postNote(request({ author: "Owner", body: "note" }), { params: Promise.resolve({ projectId: "../audit" }) })).status).toBe(400);
  expect(fetch).not.toHaveBeenCalled();
});
it("redacts upstream errors and rejects invalid success contracts", async () => {
  const fetch = vi.fn().mockResolvedValueOnce(new Response('{"detail":"password=private"}', { status: 500 })).mockResolvedValueOnce(new Response('{"items":[]}'));
  vi.stubGlobal("fetch", fetch);
  const failed = await GET(); expect(await failed.text()).not.toContain("password");
  expect((await GET()).status).toBe(502);
});
it("forwards a validated mutation with no-store and a server-only credential", async () => {
  const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ...payload, description: "", id, status: "active", created_at: "2026-10-03T00:00:00Z" }), { status: 201 }));
  vi.stubGlobal("fetch", fetch);
  const response = await POST(request(payload));
  expect(response.status).toBe(201); expect(response.headers.get("Cache-Control")).toBe("no-store");
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/v1/projects"), expect.objectContaining({ method: "POST", cache: "no-store", body: JSON.stringify({ ...payload, description: "" }) }));
  expect(await response.text()).not.toContain("token");
});
