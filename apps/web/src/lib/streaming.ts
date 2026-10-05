import { z } from "zod";

const count = z.number().int().nonnegative();
export const streamSchema = z.object({
  provider: z.enum(["sqlite", "kafka"]), topic: z.string(), consumer: z.string(),
  partitions: z.array(z.object({ partition: count, earliest: count, end: count,
    checkpoint: count, lag: count, retention_gap: z.boolean() })).max(1),
  units: count, accepted: count, quarantined: count, processed: count, delivery: z.string(),
});
export type UsageStream = z.infer<typeof streamSchema>;
export const eventBatchSchema = z.object({ events: z.array(z.object({
  event_id: z.string().regex(/^[a-z][a-z0-9-]{0,47}$/),
  units: z.number().int().min(-1000).max(1000),
}).strict()).min(1).max(100) }).strict();
export const consumeSchema = z.object({ limit: z.number().int().min(1).max(100) }).strict();
export const lakehouseSchema = z.object({ provider: z.literal("iceberg-local"), table: z.string(),
  snapshots: z.array(z.object({ snapshot_id: z.string(), committed_at_ms: count, operation: z.string(), rows: count })).max(32),
  rows: count, units: count, changed: z.boolean(), source_digest: z.string().regex(/^[a-f0-9]{64}$/),
});
export type Lakehouse = z.infer<typeof lakehouseSchema>;
