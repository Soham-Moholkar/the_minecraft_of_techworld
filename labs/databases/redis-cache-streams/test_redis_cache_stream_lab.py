"""Correctness gates over sanitized Redis lab evidence."""

import json
import pathlib
import unittest
from typing import Any

LAB_DIR = pathlib.Path(__file__).resolve().parent
EVIDENCE = LAB_DIR / ".lab-state" / "redis-cache-stream-evidence.json"


class RedisCacheStreamLabTests(unittest.TestCase):
    evidence: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_cache_miss_hit_ttl_and_expiry(self) -> None:
        cache = self.evidence["cache"]
        self.assertTrue(cache["cold_miss"])
        self.assertTrue(cache["warm_hit"])
        self.assertTrue(cache["ttl_bounded"])
        self.assertTrue(cache["expired"])

    def test_stream_recovers_unacknowledged_delivery(self) -> None:
        stream = self.evidence["stream"]
        self.assertEqual(stream["produced_count"], 3)
        self.assertGreater(stream["pending_before_claim"], 0)
        self.assertGreater(stream["consumer_b_claimed"], 0)
        self.assertEqual(stream["pending_after_claim"], 0)

    def test_watch_detects_conflict_and_fresh_retry_succeeds(self) -> None:
        transaction = self.evidence["transaction"]
        self.assertTrue(transaction["watch_conflict_detected"])
        self.assertTrue(transaction["fresh_retry_applied"])
        self.assertEqual(transaction["final_value"], 2)

    def test_acl_denies_admin_and_foreign_prefix_access(self) -> None:
        acl = self.evidence["acl"]
        self.assertEqual(acl["identity"], "atlas_lab")
        self.assertTrue(acl["flushall_denied"])
        self.assertTrue(acl["foreign_prefix_denied"])

    def test_evidence_contains_no_credentials_or_connection_details(self) -> None:
        serialized = json.dumps(self.evidence).lower()
        for forbidden in ("password", "redis://", "localhost", "atlas_lab_dev_only"):
            self.assertNotIn(forbidden, serialized)


if __name__ == "__main__":
    unittest.main()
