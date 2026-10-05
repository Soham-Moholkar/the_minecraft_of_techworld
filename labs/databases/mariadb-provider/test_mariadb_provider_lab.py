"""Correctness gates over sanitized MariaDB lab evidence."""

import json
import pathlib
import unittest
from typing import Any

LAB_DIR = pathlib.Path(__file__).resolve().parent
EVIDENCE = LAB_DIR / ".lab-state" / "mariadb-provider-evidence.json"


class MariaDBProviderLabTests(unittest.TestCase):
    evidence: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_index_preserves_results_and_is_selected(self) -> None:
        evidence = self.evidence["index"]
        self.assertTrue(evidence["result_ids_equal"])
        self.assertGreater(evidence["result_count"], 0)
        self.assertTrue(evidence["selected_index"])

    def test_plan_evidence_is_structural_and_bounded(self) -> None:
        serialized = json.dumps(self.evidence["index"])
        self.assertNotIn("tenant-1", serialized)
        self.assertNotIn("SELECT", serialized)
        self.assertLessEqual(len(self.evidence["index"]["after_access"]), 4)

    def test_repeatable_read_retains_then_refreshes_snapshot(self) -> None:
        evidence = self.evidence["repeatable_read"]
        self.assertTrue(evidence["snapshot_stable"])
        self.assertTrue(evidence["fresh_transaction_visible"])
        self.assertNotEqual(evidence["initial_balance"], evidence["fresh_transaction_balance"])

    def test_lock_wait_uses_error_code_then_retries(self) -> None:
        evidence = self.evidence["lock_recovery"]
        self.assertEqual(evidence["first_attempt_error_code"], 1205)
        self.assertTrue(evidence["retry_committed"])
        self.assertEqual(evidence["final_balance"], 150)


if __name__ == "__main__":
    unittest.main()
