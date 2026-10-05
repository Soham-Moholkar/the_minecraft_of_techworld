import { afterEach, describe, expect, it, vi } from "vitest";
import { POST } from "./route";

afterEach(() => vi.unstubAllGlobals());

const requestBody = {
  path: "README.md",
  start_line: 1,
  end_line: 2,
  intent: "explain",
  tier: "auto",
  provider: "local",
  instruction: "Explain this source.",
};

describe("repository streaming proxy", () => {
  it("preserves the normalized event stream", async () => {
    const stream = "event: delta\ndata: {\"delta\":\"hello\"}\n\n";
    const fetchMock = vi.fn().mockResolvedValue(new Response(stream, {
      headers: { "Content-Type": "text/event-stream" },
    }));
    vi.stubGlobal("fetch", fetchMock);
    const response = await POST(new Request("http://localhost/api/ai/repository/stream", {
      method: "POST",
      headers: { Origin: "http://localhost:3000", "Content-Type": "application/json" },
      body: JSON.stringify(requestBody),
    }));
    expect(response.status).toBe(200);
    expect(response.headers.get("Content-Type")).toContain("text/event-stream");
    expect(await response.text()).toBe(stream);
    expect(JSON.parse(fetchMock.mock.calls[0][1].body as string).provider).toBe("local");
  });

  it("rejects invalid input before opening an upstream stream", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const response = await POST(new Request("http://localhost/api/ai/repository/stream", {
      method: "POST",
      headers: { Origin: "http://localhost:3000", "Content-Type": "application/json" },
      body: JSON.stringify({ ...requestBody, end_line: 999 }),
    }));
    expect(response.status).toBe(400);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
