"""Regression tests for stable PostgreSQL concurrency invariants."""

from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

from postgresql_concurrency_lab import (
    DEADLOCK_SQLSTATE,
    EVIDENCE_FILENAME,
    LOCK_TIMEOUT_SQLSTATE,
    SERIALIZATION_SQLSTATE,
    STATE_FILENAME,
    initialize_schema,
    prepare_lab,
    reset_generated_state,
    reset_schema,
    run_deadlock,
    run_row_lock_timeout,
    run_serializable_retry,
)


class PostgreSQLConcurrencyLabTests(unittest.TestCase):
    """Exercise real transactions without relying on wall-clock duration."""

    def setUp(self) -> None:
        initialize_schema()

    def tearDown(self) -> None:
        # Direct unittest execution should be as disposable as run.py verify;
        # leaving the fixed schema behind would make the test suite stateful.
        reset_schema()

    def test_row_lock_returns_stable_code_then_retries(self) -> None:
        evidence = run_row_lock_timeout()
        self.assertEqual(evidence.first_attempt_sqlstate, LOCK_TIMEOUT_SQLSTATE)
        self.assertTrue(evidence.retry_succeeded)
        self.assertEqual(evidence.final_balance, 105)

    def test_deadlock_has_one_victim_and_one_commit(self) -> None:
        evidence = run_deadlock()
        self.assertEqual(evidence.deadlock_count, 1)
        self.assertEqual(evidence.committed_count, 1)
        self.assertEqual(
            sum(item.sqlstate == DEADLOCK_SQLSTATE for item in evidence.outcomes), 1
        )

    def test_serializable_failure_is_retried_from_a_fresh_decision(self) -> None:
        evidence = run_serializable_retry()
        self.assertEqual(evidence.serialization_failure_count, 1)
        self.assertEqual(
            sum(
                item.sqlstate == SERIALIZATION_SQLSTATE
                for item in evidence.first_attempt_outcomes
            ),
            1,
        )
        self.assertTrue(evidence.retry_succeeded)
        self.assertEqual(evidence.final_on_call_count, 1)

    def test_evidence_is_sanitized_and_reset_preserves_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_dir = pathlib.Path(temporary_directory) / ".lab-state"
            evidence_path = prepare_lab(state_dir)
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
            serialized = json.dumps(evidence).casefold()
            self.assertNotIn("password", serialized)
            self.assertNotIn("postgresql://", serialized)
            self.assertEqual(evidence["dataset"]["sensitivity"], "none")
            note_path = state_dir / "learner-notes.md"
            note_path.write_text("keep me\n", encoding="utf-8")
            reset_generated_state(state_dir)
            self.assertTrue(note_path.exists())
            self.assertFalse((state_dir / EVIDENCE_FILENAME).exists())
            self.assertFalse((state_dir / STATE_FILENAME).exists())


if __name__ == "__main__":
    unittest.main()
