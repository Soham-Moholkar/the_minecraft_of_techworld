import { z } from "zod";

/** Shared contracts validate provider data before it reaches product views. */
export const healthSchema = z.object({ status: z.string(), database: z.string(), version: z.string() });
export const projectInput = z.object({
  organization_id: z.uuid(), slug: z.string().min(2).max(64).regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  name: z.string().min(2).max(160), description: z.string().max(2000).default(""),
}).strict();
export const projectSchema = projectInput.extend({ id: z.uuid(), status: z.string(), created_at: z.string() });
export const projectPageSchema = z.object({ items: z.array(projectSchema).max(100), total: z.number().int().nonnegative(), limit: z.number().int(), offset: z.number().int() });
export const noteInput = z.object({ author: z.string().min(2).max(120), body: z.string().min(1).max(4000) }).strict();
export const noteSchema = noteInput.extend({ id: z.uuid(), project_id: z.uuid(), created_at: z.string() });
export const auditSchema = z.array(z.object({ id: z.uuid(), actor: z.string(), action: z.string(), target_type: z.string(), target_id: z.string(), details: z.record(z.string(), z.string()), created_at: z.string() })).max(100);
