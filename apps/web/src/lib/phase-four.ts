import { z } from "zod";

export const PROJECT_STATUS_OPTIONS = ["active", "paused", "archived"] as const;

export const databaseCacheProfileSchema = z.object({
  engine: z.literal("redis"),
  status: z.enum(["available", "unavailable"]),
  cache_state: z.enum(["hit", "miss", "bypass"]),
  project_total: z.number().int().nonnegative(),
  status_counts: z.array(z.object({
    status: z.string().trim().min(1).max(24),
    count: z.number().int().nonnegative(),
  })).max(12),
  ttl_seconds: z.number().int().min(0).max(300),
  consistency_model: z.string().trim().min(1).max(240),
  notes: z.array(z.string().trim().min(1).max(240)).max(8),
  generated_at: z.string().datetime({ offset: true }),
});

export const databaseWorkbenchRequestSchema = z.object({
  query_name: z.literal("tenant_projects_by_status"),
  status: z.enum(PROJECT_STATUS_OPTIONS),
  limit: z.number().int().min(1).max(25),
}).strict();

export const databaseWorkbenchSchema = z.object({
  engine: z.enum(["postgresql", "sqlite"]),
  query_name: z.literal("tenant_projects_by_status"),
  parameters: databaseWorkbenchRequestSchema,
  items: z.array(z.object({
    project_slug: z.string().trim().min(2).max(64),
    status: z.string().trim().min(1).max(24),
    note_count: z.number().int().nonnegative(),
    created_at: z.string().datetime({ offset: true }),
  })).max(25),
  returned_count: z.number().int().min(0).max(25),
  safety_model: z.string().trim().min(1).max(240),
  generated_at: z.string().datetime({ offset: true }),
});

export type DatabaseCacheProfile = z.infer<typeof databaseCacheProfileSchema>;
export type DatabaseWorkbench = z.infer<typeof databaseWorkbenchSchema>;
export type DatabaseWorkbenchRequest = z.infer<typeof databaseWorkbenchRequestSchema>;
