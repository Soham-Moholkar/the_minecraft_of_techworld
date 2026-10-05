import { afterEach, describe, expect, it, vi } from "vitest";
import { GET, POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

const evaluation = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  name: "Repository retrieval regression",
  report: {
    grounding_passed: true,
    citation_accuracy: 1,
    injection_detection_passed: true,
    cases: [{ id: "grounding", passed: true, hit_count: 4 }],
  },
  created_by: "owner",
  created_at: "2026-09-21T10:00:00Z",
};

describe("repository retrieval evaluation proxy", () => {
  it("validates history and persisted evaluation output", async () => {
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([evaluation])))
      .mockResolvedValueOnce(new Response(JSON.stringify(evaluation), { status: 201 })));
    expect(await (await GET()).json()).toEqual([evaluation]);
    const response = await POST(new Request(
      "http://localhost/api/ai/repository/retrieval/evaluations",
      { method: "POST", headers: { Origin: "http://localhost:3000" } },
    ));
    expect(response.status).toBe(201);
    expect(await response.json()).toEqual(evaluation);
  });

  it("blocks cross-site evaluation runs", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const response = await POST(new Request(
      "http://localhost/api/ai/repository/retrieval/evaluations",
      { method: "POST", headers: { Origin: "https://attacker.invalid" } },
    ));
    expect(response.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
