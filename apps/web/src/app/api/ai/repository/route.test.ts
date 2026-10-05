import { afterEach, describe, expect, it, vi } from "vitest";
import { GET, POST } from "./route";

const file = {
  path: "apps/api-python/src/atlas_api/repository_ai.py",
  language: "Python",
  bytes: 80,
  lines: 1,
  sha256: "b".repeat(64),
};
const explanation = {
  file,
  start_line: 1,
  end_line: 1,
  intent: "explain",
  provider: "openai",
  model: "gpt-5.6-luna",
  overview: "A complete single-line repository explanation for the contract test.",
  architecture_relations: [],
  suggested_change: null,
  lines: [{ line_number: 1, code: "value = 1", explanation: "Assigns one.", keywords: [], relations: [] }],
  usage: { input_tokens: 10, output_tokens: 5, estimated_cost_usd: 0.000008 },
};

afterEach(() => vi.unstubAllGlobals());

describe("repository AI proxy", () => {
  it("validates catalog and structured explanation contracts", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([file])))
      .mockResolvedValueOnce(new Response(JSON.stringify(explanation), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    expect(await (await GET()).json()).toEqual([file]);
    const request = new Request("http://localhost/api/ai/repository", {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: "http://localhost:3000" },
      body: JSON.stringify({
        path: file.path,
        start_line: 1,
        end_line: 1,
        intent: "explain",
        tier: "auto",
        provider: "auto",
        instruction: "Explain this line.",
      }),
    });
    const response = await POST(request);
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(explanation);
    expect(fetchMock.mock.calls[1][0]).toContain("/v1/ai/repository/explain");
  });

  it("rejects cross-site, oversized, and invalid ranges before proxying", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const crossSite = await POST(new Request("http://localhost/api/ai/repository", {
      method: "POST",
      headers: { Origin: "https://attacker.invalid", "Content-Type": "application/json" },
      body: "{}",
    }));
    expect(crossSite.status).toBe(403);
    const invalid = await POST(new Request("http://localhost/api/ai/repository", {
      method: "POST",
      headers: { Origin: "http://localhost:3000", "Content-Type": "application/json" },
      body: JSON.stringify({
        path: "README.md", start_line: 1, end_line: 121,
        intent: "explain", tier: "auto", provider: "auto", instruction: "Explain this file.",
      }),
    }));
    expect(invalid.status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
