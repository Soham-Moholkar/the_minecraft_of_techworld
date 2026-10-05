import { z } from "zod";
const receiptSchema = z.object({
  schema_version: z.literal(1), provider: z.literal("spark"), version: z.literal("4.2.0"),
  tenant: z.string().regex(/^[a-z][a-z0-9-]{0,47}$/), source_provider: z.enum(["sqlite", "kafka"]),
  source_digest: z.string().regex(/^[a-f0-9]{64}$/), rows: z.number().int().min(0).max(10000),
  units: z.number().int().min(0).max(10000000), mode: z.enum(["local", "standalone"]),
  partitions: z.number().int().min(0).max(10000), duration_ms: z.number().int().min(0).max(300000),
  finished_at: z.string().datetime({ offset: true }),
});
export const computeSchema = z.object({ receipt: receiptSchema.nullable(), source_current: z.boolean().nullable(), checked_at: z.string().datetime({ offset: true }) }).refine(value => value.receipt === null ? value.source_current === null : value.source_current !== null, "Receipt/current-state mismatch");
export type UsageCompute = z.infer<typeof computeSchema>;
