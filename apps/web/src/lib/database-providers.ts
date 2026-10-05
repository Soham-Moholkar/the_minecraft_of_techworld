import { z } from "zod";
import { isolationNameSchema } from "@/lib/concurrency-profile";

export const databaseProviderSchema = z.object({
  engine: z.enum(["postgresql", "sqlite", "mariadb"]),
  role: z.enum(["primary", "comparison"]),
  status: z.enum(["available", "unavailable"]),
  version: z.string().trim().min(1).max(64).nullable(),
  current_isolation: isolationNameSchema.nullable(),
  default_isolation: isolationNameSchema.nullable(),
  query_plan_format: z.enum(["json", "query_plan"]),
  transaction_model: z.string().trim().min(1).max(160),
  notes: z.array(z.string().trim().min(1)).max(8),
});

export const databaseProviderComparisonSchema = z.object({
  providers: z.array(databaseProviderSchema).min(1).max(4),
  generated_at: z.string().datetime({ offset: true }),
});

export type DatabaseProviderComparison = z.infer<typeof databaseProviderComparisonSchema>;
