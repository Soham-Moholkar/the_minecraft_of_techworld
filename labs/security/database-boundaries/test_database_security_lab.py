"""Regression gates for the defensive database exercise."""

import pathlib
import sqlite3
import tempfile
import unittest
from contextlib import closing

from database_security_lab import (
    ATTACK_INPUT,
    TARGET_TENANT,
    intentionally_vulnerable_search,
    prepare_database,
    reset_generated_state,
    run_exercise,
    secure_search,
    write_evidence,
)


class DatabaseSecurityTests(unittest.TestCase):
    def test_parameterization_blocks_cross_tenant_injection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = pathlib.Path(temporary) / "test.sqlite3"
            prepare_database(path)
            with closing(sqlite3.connect(path)) as connection:
                vulnerable = intentionally_vulnerable_search(
                    connection, TARGET_TENANT, ATTACK_INPUT
                )
                secure = secure_search(connection, TARGET_TENANT, ATTACK_INPUT)
            self.assertTrue(any(row[0] != TARGET_TENANT for row in vulnerable))
            self.assertEqual(secure, [])

    def test_evidence_is_redacted_and_read_only_role_denies_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            evidence = run_exercise(pathlib.Path(temporary) / "test.sqlite3")
            privilege, audit = evidence["least_privilege"], evidence["audit_event"]
            assert isinstance(privilege, dict) and isinstance(audit, dict)
            self.assertTrue(privilege["mutation_denied"])
            self.assertFalse(audit["input_recorded"])
            self.assertNotIn(ATTACK_INPUT, str(evidence))

    def test_reset_preserves_unknown_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            state_dir = pathlib.Path(temporary) / ".lab-state"
            write_evidence(state_dir)
            keep = state_dir / "learner-notes.txt"
            keep.write_text("keep", encoding="utf-8")
            reset_generated_state(state_dir)
            self.assertTrue(keep.exists())


if __name__ == "__main__":
    unittest.main()
