import { afterEach, describe, expect, it, vi } from "vitest";
import { GET, POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

const prompt = {
  id: "550e8400-e29b-41d4-a716-446655440000",
  prompt_key: "repository-explanation",
  version: 1,
  name: "Repository explanation",
  instruction: "Explain every selected line and its invariants.",
  created_by: "owner",
  created_at: "2026-09-21T10:00:00Z",
};

describe("repository prompt registry proxy", () => {
  it("validates list and immutable-create contracts", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify([prompt])))
      .mockResolvedValueOnce(new Response(JSON.stringify(prompt), { status: 201 }));
    vi.stubGlobal("fetch", fetchMock);
    expect(await (await GET()).json()).toEqual([prompt]);
    const response = await POST(new Request("http://localhost/api/ai/repository/prompts", {
      method: "POST",
      headers: { Origin: "http://localhost:3000", "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt_key: prompt.prompt_key,
        name: prompt.name,
        instruction: prompt.instruction,
      }),
    }));
    expect(response.status).toBe(201);
    expect(await response.json()).toEqual(prompt);
  });

  it("rejects cross-site prompt mutations", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const response = await POST(new Request("http://localhost/api/ai/repository/prompts", {
      method: "POST",
      headers: { Origin: "https://attacker.invalid", "Content-Type": "application/json" },
      body: "{}",
    }));
    expect(response.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
