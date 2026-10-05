import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "./route";
import { GET } from "../cache-profile/route";

afterEach(() => vi.unstubAllGlobals());

describe("database proxy boundaries", () => {
  it("rejects arbitrary SQL and cross-origin requests before calling the API", async () => {
    const upstream = vi.fn();
    vi.stubGlobal("fetch", upstream);
    const invalid = await POST(new Request("http://localhost:3000/api/database/workbench", {
      method: "POST", body: JSON.stringify({ sql: "SELECT * FROM projects" }),
    }));
    expect(invalid.status).toBe(400);
    const crossOrigin = await POST(new Request("http://localhost:3000/api/database/workbench", {
      method: "POST", headers: { origin: "https://foreign.example" }, body: "{}",
    }));
    expect(crossOrigin.status).toBe(403);
    expect(upstream).not.toHaveBeenCalled();
  });

  it("keeps upstream failure details private for both operations", async () => {
    vi.stubGlobal("fetch", vi.fn().mockImplementation(async () => new Response(
      JSON.stringify({ detail: "redis://private-credential@internal-host" }), { status: 503 },
    )));
    const cache = await GET();
    const query = await POST(new Request("http://localhost:3000/api/database/workbench", {
      method: "POST",
      body: JSON.stringify({ query_name: "tenant_projects_by_status", status: "active", limit: 5 }),
    }));
    for (const response of [cache, query]) {
      expect(response.status).toBe(503);
      expect(await response.text()).not.toContain("private-credential");
      expect(response.headers.get("cache-control")).toBe("no-store");
    }
  });
});
