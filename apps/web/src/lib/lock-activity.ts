import { z } from "zod";

export const lockActivityBucketSchema = z.object({
  mode: z.string().trim().min(1).max(64),
  granted: z.boolean(),
  count: z.number().int().nonnegative(),
});

/**
 * This contract is deliberately aggregate-only. Process IDs, relation names,
 * transaction IDs, and SQL text never cross the ordinary operator boundary.
 */
export const lockActivitySchema = z.object({
  engine: z.enum(["postgresql", "sqlite", "mariadb"]),
  available: z.boolean(),
  total_locks: z.number().int().nonnegative(),
  waiting_locks: z.number().int().nonnegative(),
  buckets: z.array(lockActivityBucketSchema).max(128),
  notes: z.array(z.string().trim().min(1)).max(16),
  generated_at: z.string().datetime({ offset: true }),
});

export type LockActivity = z.infer<typeof lockActivitySchema>;
