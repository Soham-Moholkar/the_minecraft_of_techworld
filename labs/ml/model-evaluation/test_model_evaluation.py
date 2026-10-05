"""Validate comparable evidence without enforcing machine-specific timing winners."""

import json
import pathlib
import unittest


class ModelEvaluationTests(unittest.TestCase):
    def test_models_share_holdout_and_target_source_is_not_a_feature(self) -> None:
        evidence = json.loads(
            (pathlib.Path(__file__).parent / ".lab-state" / "evidence.json").read_text(
                encoding="utf-8"
            )
        )
        report = evidence["report"]
        self.assertEqual(evidence["excluded_target_source"], "cost")
        self.assertNotIn("cost", evidence["features"])
        self.assertEqual(
            [model["model"] for model in report["models"]],
            ["logistic_regression", "decision_tree", "numpy_logistic"],
        )
        self.assertEqual(report["models"][2]["implementation"], "from-scratch")
        for model in report["models"]:
            matrix = model["metrics"]["confusion_matrix"]
            self.assertEqual(sum(sum(row) for row in matrix), report["test_rows"])
            self.assertGreaterEqual(model["metrics"]["balanced_accuracy"], 0)
            self.assertLessEqual(model["metrics"]["balanced_accuracy"], 1)
        self.assertEqual(
            {item["feature"] for item in report["feature_effects"]},
            {"requests", "day", "service"},
        )


if __name__ == "__main__":
    unittest.main()
