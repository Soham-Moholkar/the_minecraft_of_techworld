import { afterEach, describe, expect, it, vi } from "vitest";
vi.mock("server-only", () => ({}));
import { GET, POST } from "./route";
import { DELETE } from "./[memoryId]/route";
import { POST as purge } from "./purge-expired/route";
import { memoryFixture, memoryInputFixture, memorySnapshotFixture } from "@/lib/agent-memory.fixture";

afterEach(() => { vi.unstubAllGlobals(); vi.unstubAllEnvs(); });
function request(method: string, body: unknown, origin = "http://localhost:3000") {
  return new Request("http://localhost:3000/api/ai/repository/memory", {
    method, headers: { Origin: origin, "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
}

describe("operator memory proxy", () => {
  it("lists and creates with server-only authentication and no-store contracts", async () => {
    vi.stubEnv("ATLAS_DEV_TOKEN", "server-only-memory-test-token");
    const fetchMock = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify(memorySnapshotFixture)))
      .mockResolvedValueOnce(new Response(JSON.stringify(memoryFixture), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    const read = await GET();
    expect(await read.json()).toEqual(memorySnapshotFixture);
    expect(read.headers.get("Cache-Control")).toBe("no-store");
    const created = await POST(request("POST", memoryInputFixture));
    expect(created.status).toBe(201);
    expect(await created.json()).toEqual(memoryFixture);
    expect(fetchMock.mock.calls[1][1]).toMatchObject({
      method: "POST", cache: "no-store", headers: { Authorization: "Bearer server-only-memory-test-token" },
    });
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual(memoryInputFixture);
  });

  it.each([POST, purge])("rejects cross-origin mutation before fetching", async (handler) => {
    const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
    expect((await handler(request("POST", {}, "https://attacker.invalid"))).status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("validates UUID and deletion confirmation", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ removed_count: 1 })));
    vi.stubGlobal("fetch", fetchMock);
    expect((await DELETE(request("DELETE", { confirmation: "DELETE MEMORY" }), {
      params: Promise.resolve({ memoryId: "../escape" }),
    })).status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
    const response = await DELETE(request("DELETE", { confirmation: "DELETE MEMORY" }), {
      params: Promise.resolve({ memoryId: memoryFixture.id }),
    });
    expect(response.status).toBe(200);
    expect(fetchMock.mock.calls[0][0]).toMatch(new RegExp(`/memory/${memoryFixture.id}$`));
    expect(fetchMock.mock.calls[0][1].method).toBe("DELETE");
    expect((await DELETE(request("DELETE", {}), {
      params: Promise.resolve({ memoryId: memoryFixture.id }),
    })).status).toBe(400);
  });

  it("purges only expired notes through the fixed route", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ removed_count: 2 })));
    vi.stubGlobal("fetch", fetchMock);
    expect(await (await purge(request("POST", { confirmation: "REMOVE EXPIRED MEMORY" }))).json()).toEqual({ removed_count: 2 });
    expect(fetchMock.mock.calls[0][0]).toMatch(/\/memory\/purge-expired$/);
  });

  it("rejects oversized and privilege-bearing create requests locally", async () => {
    const fetchMock = vi.fn(); vi.stubGlobal("fetch", fetchMock);
    expect((await POST(request("POST", { ...memoryInputFixture, content: "x".repeat(12_001) }))).status).toBe(413);
    expect((await POST(request("POST", { ...memoryInputFixture, automatic_context: true }))).status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects automatic context and redacts upstream validation text", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ ...memorySnapshotFixture, automatic_context: true })))
      .mockResolvedValueOnce(new Response("sensitive rejected input", { status: 422 })));
    expect((await GET()).status).toBe(502);
    const response = await POST(request("POST", memoryInputFixture));
    expect(response.status).toBe(422);
    expect(await response.text()).not.toContain("sensitive rejected input");
  });

  it("redacts transport failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("sensitive path")));
    const response = await GET();
    expect(response.status).toBe(503);
    expect(await response.text()).not.toContain("sensitive path");
  });
});
