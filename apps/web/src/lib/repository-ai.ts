import { z } from "zod";

export const repositoryFileSchema = z.object({
  path: z.string().min(1).max(240),
  language: z.string().min(1).max(80),
  bytes: z.number().int().nonnegative().max(256_000),
  lines: z.number().int().positive(),
  sha256: z.string().regex(/^[0-9a-f]{64}$/),
});

const keywordSchema = z.object({
  token: z.string().min(1).max(80),
  meaning: z.string().min(2).max(300),
});

const lineSchema = z.object({
  line_number: z.number().int().positive(),
  code: z.string().max(8_000),
  explanation: z.string().min(2).max(1_200),
  keywords: z.array(keywordSchema).max(16),
  relations: z.array(z.string().max(500)).max(12),
});

export const repositoryCatalogSchema = z.array(repositoryFileSchema).max(2_000);
export const repositoryProviderHealthSchema = z.array(z.object({
  provider: z.enum(["openai", "local"]),
  configured: z.boolean(),
  reachable: z.boolean(),
  model: z.string().min(1).max(160),
  latency_ms: z.number().int().nonnegative().nullable(),
  detail: z.enum(["ready", "disabled", "unconfigured", "unreachable"]),
})).length(2);
export const repositoryPromptVersionSchema = z.object({
  id: z.string().uuid(),
  prompt_key: z.string().regex(/^[a-z][a-z0-9-]{2,63}$/),
  version: z.number().int().positive(),
  name: z.string().min(3).max(120),
  instruction: z.string().min(10).max(500),
  created_by: z.string().min(1).max(160),
  created_at: z.string().datetime(),
});
export const repositoryPromptVersionsSchema = z.array(repositoryPromptVersionSchema).max(100);
export const repositoryCitationSchema = z.object({
  id: z.string().regex(/^[0-9a-f]{16}$/),
  path: z.string().min(1).max(240),
  start_line: z.number().int().positive(),
  end_line: z.number().int().positive(),
  sha256: z.string().regex(/^[0-9a-f]{64}$/),
}).strict();
export const repositoryRetrievalHitSchema = z.object({
  citation: repositoryCitationSchema,
  snippet: z.string().max(20_000),
  lexical_score: z.number().min(0).max(1),
  embedding_score: z.number().min(0).max(1),
  final_score: z.number().min(0).max(1),
  prompt_injection_signals: z.array(z.string().regex(/^rule-[1-9][0-9]*$/)).max(8),
}).strict();
export const repositoryRetrievalSchema = z.object({
  query: z.string().min(3).max(300),
  mode: z.enum(["lexical", "hybrid"]),
  embedding_provider: z.string().min(1).max(80),
  indexed_files: z.number().int().nonnegative().max(400),
  indexed_chunks: z.number().int().nonnegative().max(2_000),
  cache_hits: z.number().int().nonnegative().max(400),
  cache_misses: z.number().int().nonnegative().max(400),
  truncated: z.boolean(),
  hits: z.array(repositoryRetrievalHitSchema).max(12),
}).strict();
const repositoryRetrievalEvaluationReportSchema = z.object({
  grounding_passed: z.boolean(),
  citation_accuracy: z.number().min(0).max(1),
  injection_detection_passed: z.boolean(),
  cases: z.array(z.object({
    id: z.string().min(1).max(80),
    passed: z.boolean(),
    hit_count: z.number().int().nonnegative().optional(),
    accuracy: z.number().min(0).max(1).optional(),
  }).strict()).max(20),
}).strict();
export const repositoryRetrievalEvaluationSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1).max(160),
  report: repositoryRetrievalEvaluationReportSchema,
  created_by: z.string().min(1).max(160),
  created_at: z.string().datetime(),
}).strict();
export const repositoryRetrievalEvaluationsSchema = z.array(
  repositoryRetrievalEvaluationSchema,
).max(50);
export const repositoryExplanationSchema = z.object({
  file: repositoryFileSchema,
  start_line: z.number().int().positive(),
  end_line: z.number().int().positive(),
  intent: z.enum(["explain", "review", "change_plan"]),
  prompt_version_id: z.string().uuid().nullable().optional(),
  provider: z.enum(["openai", "local"]),
  fallback_from: z.enum(["openai", "local"]).nullable().optional(),
  model: z.string().min(1).max(80),
  overview: z.string().min(10).max(4_000),
  architecture_relations: z.array(z.string().max(1_000)).max(20),
  suggested_change: z.string().max(4_000).nullable(),
  lines: z.array(lineSchema).min(1).max(120),
  usage: z.object({
    input_tokens: z.number().int().nonnegative(),
    output_tokens: z.number().int().nonnegative(),
    estimated_cost_usd: z.number().nonnegative(),
  }),
}).superRefine((value, context) => {
  const expected = value.end_line - value.start_line + 1;
  if (value.lines.length !== expected) {
    context.addIssue({ code: "custom", message: "line explanation is incomplete" });
  }
});

export type RepositoryFile = z.infer<typeof repositoryFileSchema>;
export type RepositoryProviderHealth = z.infer<typeof repositoryProviderHealthSchema>[number];
export type RepositoryPromptVersion = z.infer<typeof repositoryPromptVersionSchema>;
export type RepositoryRetrieval = z.infer<typeof repositoryRetrievalSchema>;
export type RepositoryRetrievalEvaluation = z.infer<typeof repositoryRetrievalEvaluationSchema>;
export type RepositoryExplanation = z.infer<typeof repositoryExplanationSchema>;

export const repositoryAIOperationsSchema = z.object({
  budget: z.object({
    monthly_limit_usd: z.number().positive(),
    committed_usd: z.number().nonnegative(),
    reserved_usd: z.number().nonnegative(),
    remaining_usd: z.number().nonnegative(),
  }).strict(),
  slo: z.object({
    sample_count: z.number().int().nonnegative().max(500),
    availability: z.number().min(0).max(1).nullable(),
    p95_seconds: z.number().nonnegative().nullable(),
    availability_target: z.number().positive().max(1),
    p95_seconds_target: z.number().positive(),
    availability_met: z.boolean().nullable(),
    latency_met: z.boolean().nullable(),
  }).strict(),
}).strict();
export type RepositoryAIOperations = z.infer<typeof repositoryAIOperationsSchema>;

export const repositoryPatchProposalSchema = z.object({
  id: z.string().uuid(),
  path: z.string().min(1).max(240),
  summary: z.string().min(5).max(200),
  rationale: z.string().min(10).max(2_000),
  status: z.enum([
    "pending", "applying", "applied", "conflicted", "failed",
    "rolling_back", "rolled_back", "rollback_conflict", "rollback_failed",
  ]),
  original_sha256: z.string().regex(/^[0-9a-f]{64}$/),
  patched_sha256: z.string().regex(/^[0-9a-f]{64}$/),
  proposal_digest: z.string().regex(/^[0-9a-f]{64}$/),
  unified_diff: z.string().min(1).max(128_000),
  start_line: z.number().int().positive(),
  end_line: z.number().int().positive(),
  proposed_by: z.string().min(1).max(160),
  approved_by: z.string().min(1).max(160).nullable(),
  failure_reason: z.string().max(120).nullable(),
  created_at: z.string().datetime(),
  approved_at: z.string().datetime().nullable(),
  applied_at: z.string().datetime().nullable(),
  rolled_back_at: z.string().datetime().nullable(),
}).strict();
export const repositoryPatchProposalsSchema = z.array(repositoryPatchProposalSchema).max(50);
export type RepositoryPatchProposal = z.infer<typeof repositoryPatchProposalSchema>;

const workflowStatusSchema = z.enum([
  "submitted", "validating", "awaiting_approval", "applied", "rolled_back",
  "conflicted", "failed",
]);
export const repositoryPatchWorkflowSchema = z.object({
  id: z.string().uuid(),
  objective: z.string().min(10).max(500),
  graph_version: z.literal(1),
  status: workflowStatusSchema,
  current_step: z.string().min(1).max(40),
  events: z.array(z.object({
    state: workflowStatusSchema,
    step: z.string().min(1).max(40),
    at: z.string().datetime(),
    detail: z.string().min(1).max(120),
  }).strict()).min(1).max(1_000),
  failure_reason: z.string().max(120).nullable(),
  created_by: z.string().min(1).max(160),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  proposal: repositoryPatchProposalSchema.nullable(),
}).strict();
export const repositoryPatchWorkflowsSchema = z.array(repositoryPatchWorkflowSchema).max(50);
export type RepositoryPatchWorkflow = z.infer<typeof repositoryPatchWorkflowSchema>;

const workflowGraphNodeSchema = z.object({
  state: workflowStatusSchema,
  title: z.string().min(1).max(80),
  kind: z.enum(["automatic", "tool", "human_gate", "terminal"]),
  tool: z.literal("guarded_patch_proposal").nullable(),
}).strict();
const workflowGraphEdgeSchema = z.object({
  source: workflowStatusSchema,
  target: workflowStatusSchema,
  step: z.string().min(1).max(40),
  condition: z.string().min(1).max(40),
  authority: z.enum(["none", "patch_approval", "rollback_approval"]),
}).strict();
export const repositoryWorkflowReplaySchema = z.object({
  workflow_id: z.string().uuid(),
  graph: z.object({
    version: z.literal(1),
    nodes: z.array(workflowGraphNodeSchema).min(1).max(20),
    edges: z.array(workflowGraphEdgeSchema).min(1).max(40),
  }).strict(),
  final_state: workflowStatusSchema,
  frames: z.array(z.object({
    sequence: z.number().int().nonnegative(),
    kind: z.enum(["transition", "evidence"]),
    event: z.object({
      state: workflowStatusSchema,
      step: z.string().min(1).max(40),
      at: z.string().datetime(),
      detail: z.string().min(1).max(120),
    }).strict(),
    condition: z.string().min(1).max(40).nullable(),
    authority: z.enum(["none", "patch_approval", "rollback_approval"]),
  }).strict()).min(1).max(1_000),
}).strict();
export type RepositoryWorkflowReplay = z.infer<typeof repositoryWorkflowReplaySchema>;

export const repositoryTestProfileSchema = z.object({
  id: z.string().regex(/^[a-z][a-z0-9-]{2,63}$/),
  version: z.number().int().positive(),
  title: z.string().min(1).max(120),
  description: z.string().min(1).max(500),
  command: z.array(z.string().min(1).max(200)).min(1).max(20),
  cwd: z.string().min(1).max(240),
  timeout_seconds: z.number().int().positive().max(600),
  memory_mb: z.number().int().positive().max(4_096),
  cpus: z.string().regex(/^\d+(\.\d+)?$/),
  pids_limit: z.number().int().positive().max(1_024),
  output_limit_bytes: z.number().int().positive().max(1_048_576),
  network: z.literal("none"),
  checkout: z.literal("staged-read-only"),
}).strict();
export const repositoryTestProfilesSchema = z.array(repositoryTestProfileSchema).max(20);
export type RepositoryTestProfile = z.infer<typeof repositoryTestProfileSchema>;

const testRunStatusSchema = z.enum([
  "pending_approval", "queued", "running", "cancel_requested", "passed", "failed",
  "cancelled", "timed_out", "output_limit", "worker_failed", "interrupted",
]);
export const repositoryTestRunSchema = z.object({
  id: z.string().uuid(),
  proposal_id: z.string().uuid(),
  retry_of_id: z.string().uuid().nullable(),
  attempt: z.number().int().positive().max(100),
  profile_id: z.string().regex(/^[a-z][a-z0-9-]{2,63}$/),
  profile_version: z.number().int().positive(),
  run_digest: z.string().regex(/^[0-9a-f]{64}$/),
  status: testRunStatusSchema,
  requested_by: z.string().min(1).max(160),
  approved_by: z.string().min(1).max(160).nullable(),
  output_excerpt: z.string().max(131_072),
  output_sha256: z.string().regex(/^[0-9a-f]{64}$/).nullable(),
  output_truncated: z.boolean(),
  exit_code: z.number().int().nullable(),
  duration_ms: z.number().int().nonnegative().nullable(),
  failure_reason: z.string().max(120).nullable(),
  cancel_requested: z.boolean(),
  created_at: z.string().datetime(),
  approved_at: z.string().datetime().nullable(),
  started_at: z.string().datetime().nullable(),
  finished_at: z.string().datetime().nullable(),
}).strict();
export const repositoryTestRunsSchema = z.array(repositoryTestRunSchema).max(50);
export type RepositoryTestRun = z.infer<typeof repositoryTestRunSchema>;
