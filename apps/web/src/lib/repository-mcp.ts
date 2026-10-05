import { z } from "zod";

// Schema content is displayed as inert JSON, never compiled or used to issue calls.
const inputSchema = z.object({
  type: z.literal("object"),
  $schema: z.literal("https://json-schema.org/draft/2020-12/schema"),
  properties: z.record(z.string(), z.unknown()),
  additionalProperties: z.literal(false),
}).catchall(z.unknown());

export const repositoryMCPToolSchema = z.object({
  name: z.string().min(1).max(128).regex(/^[A-Za-z0-9_.-]+$/),
  title: z.string().min(1).max(200),
  description: z.string().min(1).max(2_000),
  inputSchema,
  policy: z.object({
    scope: z.literal("organization-owned repository"),
    required_role: z.literal("owner"),
    approval: z.string().min(1).max(2_000),
    boundary: z.string().min(1).max(2_000),
    rest_method: z.enum(["GET", "POST"]),
    rest_path: z.string().regex(/^\/v1\/ai\/repository\/[A-Za-z0-9_/{\}-]+$/),
    source: z.string().regex(/^apps\/api-python\/src\/atlas_api\/[a-z_]+\.py$/),
    required_flags: z.array(z.enum(["ATLAS_AI_PATCH_TOOLS_ENABLED", "ATLAS_AI_TEST_TOOLS_ENABLED"])).max(2),
    local_flags_enabled: z.boolean(),
  }).strict(),
}).strict();

export const repositoryMCPCatalogSchema = z.object({
  catalog_version: z.literal(1),
  specification_revision: z.literal("2026-07-28"),
  mode: z.literal("catalog-only"),
  invocation_enabled: z.literal(false),
  tools: z.array(repositoryMCPToolSchema).max(64),
}).strict().refine((catalog) => new Set(catalog.tools.map((tool) => tool.name)).size === catalog.tools.length,
  "duplicate tool names");

export type RepositoryMCPCatalog = z.infer<typeof repositoryMCPCatalogSchema>;
