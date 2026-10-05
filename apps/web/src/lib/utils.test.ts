import { describe, expect, it } from "vitest";
import { cn, compactNumber } from "./utils";

describe("frontend utilities", () => {
  it("merges conflicting utility classes", () => expect(cn("px-2", "px-4")).toBe("px-4"));
  it("formats dense operational counts", () => expect(compactNumber(12400)).toBe("12.4K"));
});

