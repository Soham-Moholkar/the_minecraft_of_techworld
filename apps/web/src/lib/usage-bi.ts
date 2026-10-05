import { z } from "zod";
export const biSchema = z.object({ provider: z.literal("superset"), dashboard_id: z.number().int().min(1).max(2147483647), title: z.string().min(1).max(240), published: z.boolean(), checked_at: z.string().datetime({ offset: true }) });
export type UsageBi = z.infer<typeof biSchema>;
