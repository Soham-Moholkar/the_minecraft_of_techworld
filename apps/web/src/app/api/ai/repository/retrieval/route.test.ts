import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

const retrieval = {
  query: "transaction retry invariant",
  mode: "hybrid",
  embedding_provider: "hashing-v1",
  indexed_files: 2,
  indexed_chunks: 3,
  cache_hits: 1,
  cache_misses: 1,
  truncated: false,
  hits: [{
    citation: {
      id: "0123456789abcdef",
      path: "apps/service.py",
      start_line: 1,
      end_line: 12,
      sha256: "a".repeat(64),
    },
    snippet: "def retry_transaction():",
    lexical_score: 0.8,
    embedding_score: 0.7,
    final_score: 0.76,
    prompt_injection_signals: [],
  }],
};

describe("repository retrieval proxy", () => {
  it("validates the bounded hybrid result", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(retrieval)));
    vi.stubGlobal("fetch", fetchMock);
    const response = await POST(new Request("http://localhost/api/ai/repository/retrieval", {
      method: "POST",
      headers: { Origin: "http://localhost:3000", "Content-Type": "application/json" },
      body: JSON.stringify({ query: retrieval.query, top_k: 6, mode: "hybrid" }),
    }));
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(retrieval);
    expect(fetchMock.mock.calls[0][0]).toContain("/v1/ai/repository/retrieval/search");
  });

  it("rejects cross-site and malformed requests before upstream", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const crossSite = await POST(new Request("http://localhost/api/ai/repository/retrieval", {
      method: "POST",
      headers: { Origin: "https://attacker.invalid" },
      body: JSON.stringify({ query: retrieval.query }),
    }));
    const malformed = await POST(new Request("http://localhost/api/ai/repository/retrieval", {
      method: "POST",
      headers: { Origin: "http://localhost:3000" },
      body: JSON.stringify({ query: "x" }),
    }));
    expect(crossSite.status).toBe(403);
    expect(malformed.status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
