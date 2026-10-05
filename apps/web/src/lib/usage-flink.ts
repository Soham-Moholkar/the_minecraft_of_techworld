import { z } from "zod";
export const flinkSchema = z.object({
  provider: z.literal("flink"), job_id: z.string().regex(/^[a-f0-9]{32}$/),
  state: z.enum(["INITIALIZING", "CREATED", "RUNNING", "FAILING", "FAILED", "CANCELLING", "CANCELED", "FINISHED", "RESTARTING", "SUSPENDED", "RECONCILING"]),
  checkpoints: z.object({ completed: z.number().int().min(0).max(10000000), failed: z.number().int().min(0).max(10000000), in_progress: z.number().int().min(0).max(1000) }),
  vertices: z.array(z.object({ vertex_id: z.string().regex(/^[a-f0-9]{32}$/), level: z.enum(["ok", "low", "high"]).nullable() })).max(3),
  checked_at: z.string().datetime({ offset: true }),
});
export type UsageFlink = z.infer<typeof flinkSchema>;
