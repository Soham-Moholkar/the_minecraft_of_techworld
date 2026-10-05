import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import TestCenterPage from "./page";

vi.mock("@/data/quality-snapshot.json", () => ({ default: {
  generated_at: "2026-10-04T10:00:00Z",
  summary: { passed: 1, failed: 0, not_run: 1, total: 2 },
  gates: [
    { id: "old-pass", name: "Earlier API check", command: "owned-api-check", status: "passed", duration_ms: 100, executed_at: "2026-10-03T08:00:00Z" },
    { id: "runtime", name: "Runtime acceptance", command: "owned-runtime-check", status: "not_run", duration_ms: 0 },
  ],
} }));
afterEach(cleanup);

it("retains original check dates and distinguishes unexecuted gates from a fresh snapshot", () => {
  render(<TestCenterPage/>);
  expect(screen.getByText("2026-10-03T08:00:00Z")).toHaveAttribute("datetime", "2026-10-03T08:00:00Z");
  expect(screen.getByText("No recorded check")).toBeVisible();
  expect(screen.getByText(/Generated 2026-10-04T10:00:00Z/)).toBeVisible();
  expect(screen.getByText("not_run")).toBeVisible();
});
