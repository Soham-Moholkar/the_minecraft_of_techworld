"""Verify measured scale evidence, never enforce machine-specific timing winners."""

import json
import pathlib
import unittest


class ScienceQualityTests(unittest.TestCase):
    def test_scale_reports_prove_quality_counts_and_parity(self) -> None:
        path = pathlib.Path(__file__).parent / ".lab-state" / "evidence.json"
        evidence = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            [item["rows"] for item in evidence["scale_reports"]], [100, 1000, 5000]
        )
        for report in evidence["scale_reports"]:
            profile = report["profile"]
            self.assertEqual(profile["valid_rows"], report["rows"] - 2)
            self.assertEqual(profile["invalid_rows"], 1)
            self.assertEqual(profile["duplicate_rows"], 1)
            self.assertEqual(
                sum(bin["count"] for bin in profile["histogram"]), profile["valid_rows"]
            )
            for engine in profile["engines"]:
                self.assertTrue(engine["matches_reference"])
                self.assertGreaterEqual(engine["p95_ms"], engine["p50_ms"])


if __name__ == "__main__":
    unittest.main()
