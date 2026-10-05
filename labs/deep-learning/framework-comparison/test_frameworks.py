"""Validate the actual worker artifact, not a mocked tensor library."""
import json
from pathlib import Path
import unittest

class FrameworkEvidence(unittest.TestCase):
    def test_comparison(self):
        report = json.loads((Path(__file__).parent / ".lab-state/evidence.json").read_text())["report"]
        self.assertEqual(len(report["models"]), 5)
        self.assertTrue(report["tensorflow_version"])
        for model in report["models"][-2:]:
            curve = model["training_curve"]
            self.assertEqual(len(curve), 80)
            self.assertLess(curve[-1]["loss"], curve[0]["loss"])
            self.assertEqual(sum(map(sum, model["metrics"]["confusion_matrix"])), report["test_rows"])
            self.assertGreaterEqual(model["metrics"]["balanced_accuracy"], 0.65)
