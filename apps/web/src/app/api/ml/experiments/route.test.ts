import { afterEach, describe, expect, it, vi } from "vitest";
import { GET, POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

describe("model experiment proxy boundaries", () => {
  it("rejects invalid IDs, cross-origin mutations, and oversized streams locally", async () => {
    const upstream = vi.fn();
    vi.stubGlobal("fetch", upstream);
    const invalidId = await GET(new Request("http://localhost:3000/api/ml/experiments?id=bad"));
    const crossOrigin = await POST(new Request("http://localhost:3000/api/ml/experiments", {
      method: "POST", headers: { origin: "https://foreign.example" }, body: "{}",
    }));
    const oversized = await POST(new Request("http://localhost:3000/api/ml/experiments", {
      method: "POST", body: "x".repeat(4097),
    }));
    expect(invalidId.status).toBe(400);
    expect(crossOrigin.status).toBe(403);
    expect(oversized.status).toBe(413);
    expect(upstream).not.toHaveBeenCalled();
  });

  it("validates the fixed request shape before calling the API", async () => {
    const upstream = vi.fn();
    vi.stubGlobal("fetch", upstream);
    const response = await POST(new Request("http://localhost:3000/api/ml/experiments", {
      method: "POST", body: JSON.stringify({
        name: "Unsafe parameters", dataset_id: "82744b4c-a496-4a9f-a9c3-e47445d7f6b0",
        max_depth: 100,
      }),
    }));
    expect(response.status).toBe(400);
    expect(response.headers.get("cache-control")).toBe("no-store");
    expect(upstream).not.toHaveBeenCalled();
  });

  it("redacts upstream details and rejects malformed success responses", async () => {
    const upstream = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({
        detail: "postgresql://private-credential@internal-host",
      }), { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ unexpected: true })));
    vi.stubGlobal("fetch", upstream);
    const unavailable = await GET(new Request("http://localhost:3000/api/ml/experiments"));
    const malformed = await GET(new Request("http://localhost:3000/api/ml/experiments"));
    expect(unavailable.status).toBe(503);
    expect(await unavailable.text()).not.toContain("private-credential");
    expect(unavailable.headers.get("cache-control")).toBe("no-store");
    expect(malformed.status).toBe(502);
  });
});
