import { z } from "zod";

export const memoryCreateSchema = z.object({
  title: z.string().trim().min(3).max(120),
  content: z.string().trim().min(10).max(2_000),
  provenance: z.string().trim().min(3).max(240),
  retention_days: z.union([z.literal(1), z.literal(7), z.literal(30)]),
  confirmation: z.literal("NO SECRETS OR APPROVALS"),
}).strict();
export const memoryDeleteSchema = z.object({ confirmation: z.literal("DELETE MEMORY") }).strict();
export const memoryPurgeSchema = z.object({ confirmation: z.literal("REMOVE EXPIRED MEMORY") }).strict();
export const memoryReadSchema = z.object({
  id: z.string().uuid(), title: z.string().min(3).max(120), content: z.string().min(10).max(2_000),
  provenance: z.string().min(3).max(240), created_by: z.string().max(160),
  created_at: z.string().datetime({ offset: true }), expires_at: z.string().datetime({ offset: true }),
}).strict();
export const memorySnapshotSchema = z.object({
  items: z.array(memoryReadSchema).max(50), expired_count: z.number().int().min(0).max(50),
  capacity: z.literal(50), mode: z.literal("operator-managed"), automatic_context: z.literal(false),
}).strict();
export const memoryRemovalSchema = z.object({ removed_count: z.number().int().min(0).max(50) }).strict();
export type MemoryRecord = z.infer<typeof memoryReadSchema>;
export type MemorySnapshot = z.infer<typeof memorySnapshotSchema>;
