import { afterEach, describe, expect, it, vi } from "vitest";
import { GET, POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

describe("applied AI proxy boundaries", () => {
  it("rejects invalid identifiers, cross-origin writes, and extra fields", async () => {
    const upstream = vi.fn(); vi.stubGlobal("fetch", upstream);
    expect((await GET(new Request("http://localhost:3000/api/ml/applied-experiments?id=bad"))).status).toBe(400);
    expect((await POST(new Request("http://localhost:3000/api/ml/applied-experiments", {
      method: "POST", headers: { origin: "https://foreign.example" }, body: "{}",
    }))).status).toBe(403);
    expect((await POST(new Request("http://localhost:3000/api/ml/applied-experiments", {
      method: "POST", body: JSON.stringify({ name: "Unsafe", epochs: 5000 }),
    }))).status).toBe(400);
    expect(upstream).not.toHaveBeenCalled();
  });

  it("redacts upstream errors and rejects malformed success payloads", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "private worker stderr" }), { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ bad: true }))));
    const unavailable = await GET(new Request("http://localhost:3000/api/ml/applied-experiments"));
    expect(unavailable.status).toBe(503);
    expect(await unavailable.text()).not.toContain("private worker stderr");
    expect((await GET(new Request("http://localhost:3000/api/ml/applied-experiments"))).status).toBe(502);
  });
});
