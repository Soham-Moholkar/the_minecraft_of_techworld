import { afterEach, describe, expect, it, vi } from "vitest";
import { GET } from "./route";

afterEach(() => vi.unstubAllGlobals());

const operations = {
  budget: {
    monthly_limit_usd: 25,
    committed_usd: 1.25,
    reserved_usd: 0.25,
    remaining_usd: 23.5,
  },
  slo: {
    sample_count: 12,
    availability: 1,
    p95_seconds: 2.5,
    availability_target: 0.99,
    p95_seconds_target: 30,
    availability_met: true,
    latency_met: true,
  },
};

describe("repository AI operations proxy", () => {
  it("validates tenant budget and rolling SLO evidence", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(operations))));
    const response = await GET();
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual(operations);
  });

  it("rejects malformed operational evidence", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ budget: {} }))));
    expect((await GET()).status).toBe(502);
  });
});
