"""Validate the suite artifact produced by the real isolated worker."""

import json
from pathlib import Path
import unittest


class AppliedEvidence(unittest.TestCase):
    def test_all_families_have_improving_finite_evidence(self) -> None:
        report = json.loads((Path(__file__).parent / ".lab-state/evidence.json").read_text())
        self.assertEqual(
            {task["task"] for task in report["tasks"]},
            {"computer_vision", "time_series", "nlp_attention", "recommendation"},
        )
        for task in report["tasks"]:
            self.assertLess(task["training_curve"][-1]["loss"], task["training_curve"][0]["loss"])
            if task["higher_is_better"]:
                self.assertGreater(task["model_score"], task["baseline_score"])
            else:
                self.assertLess(task["model_score"], task["baseline_score"])


if __name__ == "__main__":
    unittest.main()
