import { afterEach, expect, it, vi } from "vitest";
import { GET, POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

it("bounds imports independently of Content-Length and rejects foreign origins", async () => {
  const upstream = vi.fn();
  vi.stubGlobal("fetch", upstream);
  const oversized = await POST(new Request("http://localhost:3000/api/datasets", {
    method: "POST", body: "x".repeat(300001),
  }));
  expect(oversized.status).toBe(413);
  const foreign = await POST(new Request("http://localhost:3000/api/datasets", {
    method: "POST", headers: { origin: "https://foreign.example" }, body: "{}",
  }));
  expect(foreign.status).toBe(403);
  expect(upstream).not.toHaveBeenCalled();
});

it("rejects invalid IDs and strips upstream error details", async () => {
  const upstream = vi.fn().mockResolvedValue(new Response(JSON.stringify({
    detail: "postgresql://private-credential@internal-host",
  }), { status: 503 }));
  vi.stubGlobal("fetch", upstream);
  expect((await GET(new Request("http://localhost:3000/api/datasets?id=invalid"))).status).toBe(400);
  expect(upstream).not.toHaveBeenCalled();
  const response = await GET(new Request("http://localhost:3000/api/datasets"));
  expect(response.status).toBe(503);
  expect(response.headers.get("cache-control")).toBe("no-store");
  expect(await response.text()).not.toContain("private-credential");
});
