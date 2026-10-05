import { z } from "zod";
export const dagSchema = z.object({
  provider: z.literal("airflow"), dag_id: z.literal("atlas_usage_rollup"), checked_at: z.string(),
  runs: z.array(z.object({ dag_run_id: z.string().max(240), state: z.enum(["queued", "running", "success", "failed"]), start_date: z.string().nullable().optional(), end_date: z.string().nullable().optional() })).max(5),
  latest_tasks: z.array(z.object({ task_id: z.enum(["consume", "validate_parquet", "refresh_lakehouse"]), state: z.enum(["none", "scheduled", "queued", "running", "success", "failed", "up_for_retry", "up_for_reschedule", "upstream_failed", "skipped", "deferred", "removed", "restarting"]), try_number: z.number().int().min(0).max(1000) })).max(3),
});
export type UsageDag = z.infer<typeof dagSchema>;
