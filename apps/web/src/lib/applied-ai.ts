import { z } from "zod";

const score = z.number().finite().nonnegative();
const taskSchema = z.object({
  task: z.enum(["computer_vision", "time_series", "nlp_attention", "recommendation"]),
  architecture: z.string().min(2).max(80), baseline: z.string().min(2).max(80),
  metric: z.enum(["accuracy", "mae", "hit_rate_at_3"]), higher_is_better: z.boolean(),
  model_score: score, baseline_score: score,
  training_curve: z.array(z.object({
    epoch: z.number().int().positive().max(60), loss: score,
  })).min(1).max(60),
  train_examples: z.number().int().positive().max(1000),
  test_examples: z.number().int().positive().max(1000),
});
const summary = {
  id: z.string().uuid(), name: z.string().min(2).max(120),
  created_at: z.string().datetime({ offset: true }), tasks: z.literal(4),
  improved_tasks: z.number().int().min(0).max(4),
};
export const appliedSummarySchema = z.object(summary);
export const appliedListSchema = z.array(appliedSummarySchema).max(50);
export const appliedExperimentSchema = z.object(summary).extend({
  report: z.object({
    suite: z.literal("phase7_applied_ai"), random_seed: z.literal(42),
    torch_version: z.string().min(1).max(40),
    tasks: z.array(taskSchema).length(4).superRefine((tasks, context) => {
      const names = new Set(tasks.map((item) => item.task));
      if (names.size !== 4) context.addIssue({ code: "custom", message: "suite is incomplete" });
    }),
    caveats: z.array(z.string().max(240)).min(1).max(8),
  }),
});
export type AppliedExperiment = z.infer<typeof appliedExperimentSchema>;
export type AppliedSummary = z.infer<typeof appliedSummarySchema>;

export const taskLabel: Record<AppliedExperiment["report"]["tasks"][number]["task"], string> = {
  computer_vision: "Computer vision",
  time_series: "Time series",
  nlp_attention: "NLP + attention",
  recommendation: "Recommendation",
};
