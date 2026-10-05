import { z } from "zod";

export const PROJECT_QUERY_NAME = "tenant_projects_by_status" as const;

export const projectStatusSchema = z
  .string()
  .trim()
  .min(1)
  .max(24)
  .regex(/^[a-z][a-z0-9_-]*$/, "status must use lowercase letters, numbers, underscores, or hyphens");

export const queryPlanSchema = z.object({
  engine: z.enum(["postgresql", "sqlite", "mariadb"]),
  query_name: z.literal(PROJECT_QUERY_NAME),
  parameters: z.object({ status: projectStatusSchema }),
  nodes: z.array(
    z.object({
      operation: z.string().min(1),
      relation: z.string().nullable(),
      detail: z.string().min(1),
      estimated_rows: z.number().nonnegative().nullable(),
      estimated_cost: z.number().nonnegative().nullable(),
    }),
  ),
  recommendations: z.array(z.string().min(1)),
  generated_at: z.string().datetime({ offset: true }),
});

export type QueryPlan = z.infer<typeof queryPlanSchema>;

/**
 * The database accepts any validated project status because status is product
 * data, not an enum in storage. These common options keep the operational UI
 * deliberate while the BFF still safely supports future status values.
 */
export const PROJECT_STATUS_OPTIONS = ["active", "paused", "archived"] as const;
