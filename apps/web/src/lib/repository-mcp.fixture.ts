/** Synthetic contract evidence for deterministic UI/BFF tests, never production data. */
export const mcpCatalogFixture = {
  catalog_version: 1,
  specification_revision: "2026-07-28",
  mode: "catalog-only",
  invocation_enabled: false,
  tools: [
    {
      name: "repository.patch.apply", title: "Apply reviewed patch",
      description: "Apply only a reviewed exact-digest proposal.",
      inputSchema: {
        $schema: "https://json-schema.org/draft/2020-12/schema", type: "object",
        additionalProperties: false,
        properties: { confirmation: { const: "APPLY EXACT PATCH" }, proposal_id: { type: "string", format: "uuid" } },
        required: ["confirmation", "proposal_id"],
      },
      policy: {
        scope: "organization-owned repository", required_role: "owner",
        approval: "Exact proposal digest and APPLY EXACT PATCH.",
        boundary: "Allowlisted local write; never arbitrary shell execution.",
        rest_method: "POST", rest_path: "/v1/ai/repository/patches/{proposal_id}/approve",
        source: "apps/api-python/src/atlas_api/agent_patches.py",
        required_flags: ["ATLAS_AI_PATCH_TOOLS_ENABLED"], local_flags_enabled: false,
      },
    },
    {
      name: "repository.test.approve", title: "Approve isolated test",
      description: "Queue a separately approved fixed profile.",
      inputSchema: {
        $schema: "https://json-schema.org/draft/2020-12/schema", type: "object",
        additionalProperties: false, properties: { confirmation: { const: "RUN ISOLATED TEST PROFILE" } },
        required: ["confirmation"],
      },
      policy: {
        scope: "organization-owned repository", required_role: "owner",
        approval: "Exact run digest and RUN ISOLATED TEST PROFILE.",
        boundary: "Networkless resource-bounded Docker; absence fails closed.",
        rest_method: "POST", rest_path: "/v1/ai/repository/test-runs/{run_id}/approve",
        source: "apps/api-python/src/atlas_api/agent_tests.py",
        required_flags: ["ATLAS_AI_PATCH_TOOLS_ENABLED", "ATLAS_AI_TEST_TOOLS_ENABLED"], local_flags_enabled: true,
      },
    },
  ],
};
