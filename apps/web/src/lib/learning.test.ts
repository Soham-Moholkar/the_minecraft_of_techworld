import { describe, expect, it } from "vitest";
import { completionPercent, nextLabStatus } from "./learning";

describe("learning state", () => {
  it("bounds progress to a percentage", () => {
    expect(completionPercent(4, 3)).toBe(75);
    expect(completionPercent(4, 8)).toBe(100);
    expect(completionPercent(0, 0)).toBe(0);
  });

  it("requires a started lab before recording a pass", () => {
    expect(nextLabStatus("idle", "test")).toBe("idle");
    expect(nextLabStatus("idle", "start")).toBe("ready");
    expect(nextLabStatus("ready", "test")).toBe("passed");
    expect(nextLabStatus("passed", "reset")).toBe("idle");
  });
});
