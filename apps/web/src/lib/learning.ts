export function completionPercent(total: number, completed: number) {
  if (total <= 0) return 0;
  return Math.round((Math.min(Math.max(completed, 0), total) / total) * 100);
}

export function nextLabStatus(current: "idle" | "ready" | "passed", action: "start" | "test" | "reset") {
  if (action === "reset") return "idle" as const;
  if (action === "start") return "ready" as const;
  return current === "ready" || current === "passed" ? "passed" as const : current;
}
