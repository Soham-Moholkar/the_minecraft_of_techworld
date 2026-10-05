import { z } from "zod";
import { deploymentBudgetSchema } from "@/lib/deployment-review";
const digest = z.string().regex(/^[a-f0-9]{64}$/);
export const infrastructurePlanSchema = z.object({
  checked_at: z.string().datetime({ offset: true }), source_current: z.boolean().nullable(),
  receipt: z.object({ schema_version: z.literal(1), engine: z.literal("opentofu"), engine_version: z.literal("1.13.0"), scope: z.literal("local-metadata"), state_baseline: z.literal("empty-disposable-fixture"), created: z.literal(1), changed: z.literal(0), destroyed: z.literal(0), configuration_digest: digest, plan_digest: digest, input: z.object({ namespace: z.literal("atlas-dev"), manifest_digest: digest, budget: deploymentBudgetSchema }), finished_at: z.string().datetime({ offset: true }) }).nullable(),
}).superRefine((value, context) => {
  if ((value.receipt === null) !== (value.source_current === null)) context.addIssue({code:"custom",message:"Receipt and lineage mismatch"});
});
export type InfrastructurePlan = z.infer<typeof infrastructurePlanSchema>;
