"""Stable gates for benchmark structure and result equivalence."""

import pathlib
import tempfile
import unittest

from provider_benchmark_lab import reset_generated_state, run_suite, write_evidence


class ProviderBenchmarkTests(unittest.TestCase):
    def test_suite_records_required_evidence_without_timing_thresholds(self) -> None:
        report = run_suite(row_count=1_200)
        results, correctness, caveats = (
            report["results"],
            report["correctness"],
            report["caveats"],
        )
        assert isinstance(results, list) and isinstance(correctness, dict)
        assert isinstance(caveats, list)
        self.assertEqual(len(results), 3)
        self.assertTrue(correctness["identical_checksums"])
        self.assertTrue(correctness["identical_result_counts"])
        for result in results:
            self.assertGreater(result["p50_ms"], 0)
            self.assertGreaterEqual(result["p95_ms"], result["p50_ms"])
            self.assertGreater(result["operations_per_second"], 0)
        self.assertGreaterEqual(len(caveats), 4)

    def test_lifecycle_writes_and_removes_only_known_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = pathlib.Path(temporary) / ".lab-state"
            report_path = write_evidence(state_dir)
            keep = state_dir / "learner-notes.txt"
            keep.write_text("keep", encoding="utf-8")
            self.assertTrue(report_path.exists())
            reset_generated_state(state_dir)
            self.assertTrue(keep.exists())


if __name__ == "__main__":
    unittest.main()
