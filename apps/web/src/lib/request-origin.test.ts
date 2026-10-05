import { afterEach, expect, it, vi } from "vitest";
import { allowsMutation } from "./request-origin";

afterEach(() => vi.unstubAllEnvs());

it("allows configured public origins behind the container proxy", () => {
  vi.stubEnv("ATLAS_ALLOWED_ORIGINS", "http://localhost:3000");
  expect(allowsMutation(new Request("http://0.0.0.0:3000/api/datasets", {
    headers: { origin: "http://localhost:3000", "sec-fetch-site": "same-origin" },
  }))).toBe(true);
  expect(allowsMutation(new Request("http://0.0.0.0:3000/api/datasets", {
    headers: { origin: "https://foreign.example" },
  }))).toBe(false);
  expect(allowsMutation(new Request("http://0.0.0.0:3000/api/datasets", {
    headers: { "sec-fetch-site": "cross-site" },
  }))).toBe(false);
});
