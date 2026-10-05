import { z } from "zod";

const finiteRate = z.number().finite().min(0).max(1);
const metricsSchema = z.object({
  accuracy: finiteRate, balanced_accuracy: finiteRate, precision: finiteRate,
  recall: finiteRate, f1: finiteRate, roc_auc: finiteRate,
  confusion_matrix: z.array(z.array(z.number().int().nonnegative()).length(2)).length(2),
});
const expectedModels = new Set(["logistic_regression", "decision_tree", "numpy_logistic"]);
const modelEvidenceSchema = z.object({
  model: z.enum(["logistic_regression", "decision_tree", "numpy_logistic", "pytorch_mlp", "keras_mlp"]),
  implementation: z.enum(["scikit-learn", "from-scratch", "pytorch", "tensorflow-keras"]),
  fit_ms: z.number().finite().nonnegative(), metrics: metricsSchema,
  training_curve: z.array(z.object({ epoch: z.number().int().min(1).max(80),
    loss: z.number().finite().nonnegative() })).max(80).default([]),
});
const summaryFields = {
  id: z.string().uuid(), dataset_id: z.string().uuid(),
  dataset_name: z.string().min(2).max(120), name: z.string().min(2).max(120),
  created_at: z.string().datetime({ offset: true }), best_model: z.string().max(40),
  best_balanced_accuracy: finiteRate,
};
export const experimentSummarySchema = z.object(summaryFields);
export const experimentSchema = z.object(summaryFields).extend({
  report: z.object({
    task: z.literal("high_cost_classification"), target_definition: z.string().max(160),
    training_rows: z.number().int().positive().max(5000),
    test_rows: z.number().int().positive().max(5000), positive_rate: finiteRate,
    random_seed: z.number().int(), sklearn_version: z.string().max(40),
    torch_version: z.string().max(40).nullable().optional(),
    tensorflow_version: z.string().max(40).nullable().optional(),
    keras_version: z.string().max(40).nullable().optional(),
    models: z.array(modelEvidenceSchema).min(3).max(5).superRefine((models, context) => {
      const names = new Set(models.map((model) => model.model));
      if (names.size !== models.length || (names.has("keras_mlp") && !names.has("pytorch_mlp")) || [...expectedModels].some((name) => !names.has(name as typeof models[number]["model"]))) {
        context.addIssue({ code: "custom", message: "model comparison is incomplete" });
      }
      for (const model of models) {
        const expected = model.model === "keras_mlp" ? "tensorflow-keras" : model.model === "pytorch_mlp" ? "pytorch"
          : model.model === "numpy_logistic" ? "from-scratch" : "scikit-learn";
        if (model.implementation !== expected || (["pytorch_mlp", "keras_mlp"].includes(model.model) &&
          (model.training_curve.length !== 80 || model.training_curve.some((point, i) => point.epoch !== i + 1)))) {
          context.addIssue({ code: "custom", message: "invalid model implementation or curve" });
        }
      }
    }),
    feature_effects: z.array(z.object({
      feature: z.enum(["requests", "day", "service"]),
      importance_mean: z.number().finite(), importance_stddev: z.number().finite().nonnegative(),
    })).length(3),
    caveats: z.array(z.string().max(240)).max(8),
  }),
});
export const experimentListSchema = z.array(experimentSummarySchema).max(100);
export type Experiment = z.infer<typeof experimentSchema>;
export type ExperimentSummary = z.infer<typeof experimentSummarySchema>;

export function displayModel(value: string) {
  return value.replaceAll("_", " ");
}
