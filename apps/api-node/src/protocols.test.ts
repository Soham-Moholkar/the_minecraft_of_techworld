import assert from "node:assert/strict";
import test from "node:test";
import {
  authenticated,
  boundedLimit,
  executeProjectGraphQL,
  type ProjectProvider,
} from "./protocols.js";

const provider: ProjectProvider = {
  async list(limit) {
    return [{
      id: "c28f2183-251d-4a8e-9540-abfde244a7fe",
      slug: "risk-console",
      name: "Risk Console",
      description: "Tenant risk",
      status: "active",
      createdAt: "2026-08-27T17:30:00Z",
    }].slice(0, limit);
  },
};

test("GraphQL executes the same typed project provider contract", async () => {
  const result = await executeProjectGraphQL(
    provider,
    "query Projects($limit: Int!) { projects(limit: $limit) { slug name status } }",
    { limit: 10 },
  );
  assert.deepEqual(result.errors, undefined);
  // GraphQL response objects intentionally have null prototypes; JSON round-tripping
  // compares their public wire representation rather than implementation identity.
  assert.deepEqual(JSON.parse(JSON.stringify(result.data)), {
    projects: [{ slug: "risk-console", name: "Risk Console", status: "active" }],
  });
});

test("auth and bounded pagination fail closed", () => {
  assert.equal(authenticated("Bearer atlas-local-development-token", "atlas-local-development-token"), true);
  assert.equal(authenticated("Bearer wrong", "atlas-local-development-token"), false);
  assert.equal(boundedLimit("25"), 25);
  assert.throws(() => boundedLimit(101), /1 to 100/);
});
