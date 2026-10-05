import { z } from "zod";

const finite = z.number().finite();
const count = z.number().int().nonnegative();
export const datasetSummarySchema = z.object({
  id: z.string().uuid(), name: z.string().min(2).max(120),
  source_checksum: z.string().regex(/^[a-f0-9]{64}$/),
  created_at: z.string().datetime({ offset: true }), valid_rows: count.max(5000),
});
export const datasetSchema = datasetSummarySchema.extend({
  profile: z.object({
    input_rows: count.max(5000), valid_rows: count.max(5000), invalid_rows: count,
    duplicate_rows: count, service_count: count.max(100),
    cost_total: finite, cost_mean: finite, cost_median: finite, cost_p95: finite,
    cost_stddev: finite, mean_ci95: z.array(finite).length(2).nullable(),
    histogram: z.array(z.object({ lower: finite, upper: finite, count })).max(10),
    services: z.array(z.object({ service: z.string().max(64), cost: finite, requests: count })).max(100),
    engines: z.array(z.object({ engine: z.enum(["pandas", "polars", "duckdb"]),
      version: z.string().max(40), p50_ms: finite, p95_ms: finite,
      repetitions: count, matches_reference: z.boolean() })).length(3),
    caveats: z.array(z.string().max(240)).max(8),
    generated_at: z.string().datetime({ offset: true }),
  }),
});
export type Dataset = z.infer<typeof datasetSchema>;
export type DatasetSummary = z.infer<typeof datasetSummarySchema>;
export const datasetListSchema = z.array(datasetSummarySchema).max(100);

export const sampleCsv = "date,service,cost,requests\n" + Array.from({ length: 60 }, (_, index) =>
  `2026-09-${String(1 + index % 28).padStart(2, "0")},${["api", "worker", "search"][index % 3]},${(4 + index * 1.7).toFixed(2)},${100 + index * 23}`,
).join("\n") + "\n2026-09-01,api,4.00,100\n2026-09-02,worker,invalid,20\n";
