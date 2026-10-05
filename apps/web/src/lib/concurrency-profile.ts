import { z } from "zod";

export const isolationNameSchema = z.enum([
  "read_uncommitted",
  "read_committed",
  "repeatable_read",
  "serializable",
]);

export const isolationCapabilitySchema = z.object({
  level: isolationNameSchema,
  support: z.enum(["native", "mapped", "conditional", "unsupported"]),
  effective_level: isolationNameSchema.nullable(),
  detail: z.string().trim().min(1),
});

/**
 * The provider reports both the requested SQL isolation vocabulary and its
 * effective engine behavior. That distinction is essential for SQLite, where
 * some standard levels are aliases or conditional rather than native modes.
 */
export const concurrencyProfileSchema = z.object({
  engine: z.enum(["postgresql", "sqlite", "mariadb"]),
  current_isolation: isolationNameSchema,
  default_isolation: isolationNameSchema,
  capabilities: z.array(isolationCapabilitySchema),
  notes: z.array(z.string().trim().min(1)),
  generated_at: z.string().datetime({ offset: true }),
});

export type ConcurrencyProfile = z.infer<typeof concurrencyProfileSchema>;
