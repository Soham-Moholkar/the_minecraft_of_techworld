import { afterEach, describe, expect, it, vi } from "vitest";
import { GET } from "./route";

afterEach(() => vi.unstubAllGlobals());

describe("repository provider-health proxy", () => {
  it("validates and redacts the provider comparison contract", async () => {
    const providers = [
      { provider: "openai", configured: true, reachable: true, model: "gpt-5.6-luna", latency_ms: 42, detail: "ready" },
      { provider: "local", configured: false, reachable: false, model: "local-code-model", latency_ms: null, detail: "disabled" },
    ];
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(providers))));
    const response = await GET();
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(providers);
  });

  it("rejects malformed upstream health", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify([
      { provider: "local", configured: true, reachable: true, model: "x", latency_ms: 1, detail: "ready", url: "secret" },
    ]))));
    expect((await GET()).status).toBe(502);
  });
});
