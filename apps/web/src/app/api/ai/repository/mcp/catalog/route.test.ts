import { afterEach, describe, expect, it, vi } from "vitest";
import * as route from "./route";
import { mcpCatalogFixture } from "@/lib/repository-mcp.fixture";

afterEach(() => { vi.unstubAllGlobals(); vi.unstubAllEnvs(); });

describe("read-only MCP discovery proxy", () => {
  it("uses a fixed authenticated no-store GET and exposes no mutation handler", async () => {
    vi.stubEnv("ATLAS_DEV_TOKEN", "server-only-test-token");
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(mcpCatalogFixture)));
    vi.stubGlobal("fetch", fetchMock);
    const response = await route.GET();
    expect(response.status).toBe(200);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(await response.json()).toEqual(mcpCatalogFixture);
    expect(fetchMock.mock.calls[0][0]).toMatch(/\/v1\/ai\/repository\/mcp\/catalog$/);
    expect(fetchMock.mock.calls[0][1]).toMatchObject({
      cache: "no-store", headers: { Authorization: "Bearer server-only-test-token" },
    });
    expect(fetchMock.mock.calls[0][1].method).toBeUndefined();
    expect(Object.keys(route)).toEqual(["GET"]);
  });

  it.each([
    { ...mcpCatalogFixture, invocation_enabled: true },
    { ...mcpCatalogFixture, tools: [...mcpCatalogFixture.tools, mcpCatalogFixture.tools[0]] },
    { ...mcpCatalogFixture, tools: [{ ...mcpCatalogFixture.tools[0], policy: { ...mcpCatalogFixture.tools[0].policy, required_role: "reader" } }] },
  ])("rejects changed authority or duplicate contracts", async (payload) => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(payload))));
    expect((await route.GET()).status).toBe(502);
  });

  it("redacts upstream failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("secret host path")));
    const response = await route.GET();
    expect(response.status).toBe(503);
    expect(await response.text()).not.toContain("secret host path");
  });

  it("does not forward an unauthorized upstream body", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("sensitive detail", { status: 403 })));
    const response = await route.GET();
    expect(response.status).toBe(503);
    expect(await response.text()).not.toContain("sensitive detail");
  });
});
