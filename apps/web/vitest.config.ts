import { defineConfig } from "vitest/config";
import { fileURLToPath } from "node:url";

export default defineConfig({
  test: { environment: "jsdom", setupFiles: ["./src/test/setup.ts"] },
  // fileURLToPath decodes spaces and preserves Windows drive-letter semantics;
  // URL.pathname alone only happened to work for alias-free tests.
  resolve: { alias: {
    "@": fileURLToPath(new URL("./src", import.meta.url)),
    // Next enforces this marker during production compilation. Route unit tests
    // run without an RSC compiler, so only their environment resolves a no-op.
    "server-only": fileURLToPath(new URL("./src/test/server-only.ts", import.meta.url)),
  } },
});
