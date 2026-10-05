"""Correctness gates over sanitized MongoDB lab evidence."""

import json
import pathlib
import unittest
from typing import Any

from mongodb_document_lab import assert_lab_identity

LAB_DIR = pathlib.Path(__file__).resolve().parent
EVIDENCE = LAB_DIR / ".lab-state" / "mongodb-document-evidence.json"


class MongoDBDocumentLabTests(unittest.TestCase):
    evidence: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_compound_index_preserves_results_and_is_selected(self) -> None:
        evidence = self.evidence["index"]
        self.assertTrue(evidence["results_equal"])
        self.assertTrue(evidence["before_collection_scan"])
        self.assertTrue(evidence["selected_compound_index"])
        self.assertGreater(evidence["result_count"], 0)

    def test_reset_identity_accepts_only_the_database_scoped_lab_user(self) -> None:
        assert_lab_identity(
            {
                "authInfo": {
                    "authenticatedUsers": [
                        {"user": "atlas_document_lab", "db": "atlas_document_lab"}
                    ]
                }
            }
        )
        with self.assertRaisesRegex(RuntimeError, "dedicated atlas_document_lab"):
            assert_lab_identity(
                {"authInfo": {"authenticatedUsers": [{"user": "atlas_root", "db": "admin"}]}}
            )

    def test_plan_evidence_contains_no_query_or_tenant_values(self) -> None:
        serialized = json.dumps(self.evidence["index"])
        self.assertNotIn("tenant-1", serialized)
        self.assertNotIn("parsedQuery", serialized)
        self.assertNotIn("filter", serialized)

    def test_schema_validation_rejects_invalid_document_by_code(self) -> None:
        evidence = self.evidence["validation"]
        self.assertTrue(evidence["invalid_document_rejected"])
        self.assertEqual(evidence["error_code"], 121)

    def test_optimistic_version_filter_rejects_stale_writer(self) -> None:
        evidence = self.evidence["optimistic_update"]
        self.assertTrue(evidence["first_update_applied"])
        self.assertTrue(evidence["stale_update_rejected"])
        self.assertTrue(evidence["fresh_retry_applied"])
        self.assertEqual(evidence["final_available"], 7)
        self.assertEqual(evidence["final_version"], 3)


if __name__ == "__main__":
    unittest.main()
