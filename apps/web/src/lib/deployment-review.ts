import { z } from "zod";
export const deploymentBudgetSchema = z.object({ cpu_request_millicores: z.number().int().nonnegative(), cpu_limit_millicores: z.number().int().nonnegative(), memory_request_mib: z.number().int().nonnegative(), memory_limit_mib: z.number().int().nonnegative(), storage_mib: z.number().int().nonnegative(), replicas: z.number().int().nonnegative() });

// This observation contains no manifest values, secrets or cluster credentials.
export const deploymentReviewSchema = z.object({
  namespace: z.literal("atlas-dev"), release: z.literal("atlas"),
  checked_at: z.string().datetime({ offset: true }), manifest_digest: z.string().regex(/^[a-f0-9]{64}$/),
  status: z.enum(["passed", "blocked"]), cluster_status: z.literal("not_checked"),
  resources: z.array(z.object({ kind: z.string().max(64), name: z.string().max(64), retained: z.boolean(), matches_contract: z.boolean() })).max(32),
  findings: z.array(z.object({ code: z.enum(["resource-contract", "inventory-contract"]), message: z.string().max(240) })).max(33),
  budget: deploymentBudgetSchema.nullable(),
  teardown: z.array(z.string().max(240)).max(32), retained: z.array(z.string().max(120)).max(32),
});
export type DeploymentReview = z.infer<typeof deploymentReviewSchema>;
