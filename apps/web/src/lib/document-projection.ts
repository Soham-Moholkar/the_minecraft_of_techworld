import { z } from "zod";

const projectionItemSchema = z.object({
  project_slug: z.string().trim().min(2).max(64),
  status: z.string().trim().min(1).max(24),
  note_count: z.number().int().nonnegative(),
  created_at: z.string().datetime({ offset: true }),
});

export const documentProjectionSnapshotSchema = z.object({
  engine: z.literal("mongodb"),
  status: z.enum(["available", "empty", "unavailable"]),
  document_count: z.number().int().nonnegative(),
  published_at: z.string().datetime({ offset: true }).nullable(),
  items: z.array(projectionItemSchema).max(25),
  index_strategy: z.string().trim().min(1).max(200),
  consistency_model: z.string().trim().min(1).max(200),
  notes: z.array(z.string().trim().min(1).max(240)).max(8),
  generated_at: z.string().datetime({ offset: true }),
});

export const documentProjectionPublishSchema = z.object({
  engine: z.literal("mongodb"),
  published_count: z.number().int().nonnegative(),
  removed_count: z.number().int().nonnegative(),
  published_at: z.string().datetime({ offset: true }),
});

export type DocumentProjectionSnapshot = z.infer<typeof documentProjectionSnapshotSchema>;
export type DocumentProjectionPublish = z.infer<typeof documentProjectionPublishSchema>;
