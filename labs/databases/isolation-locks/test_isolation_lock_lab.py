"""Regression tests for SQLite snapshot, lock, and reset behavior."""

from __future__ import annotations

import json
import pathlib
import sqlite3
import tempfile
import unittest

from isolation_lock_lab import (
    BUSY_TIMEOUT_MS,
    DATABASE_FILENAME,
    GENERATED_FILENAMES,
    initialize_database,
    prepare_lab,
    reset_generated_state,
    run_reader_snapshot,
    run_writer_lock,
)


class IsolationLockExperimentTests(unittest.TestCase):
    """Assert logical outcomes without depending on scheduler or disk timings."""

    def test_reader_keeps_snapshot_until_transaction_ends(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = pathlib.Path(temporary_directory) / DATABASE_FILENAME
            initialize_database(database_path)

            evidence = run_reader_snapshot(database_path)

            self.assertEqual(evidence.initial_value, "disabled")
            self.assertEqual(evidence.value_inside_original_snapshot, "disabled")
            self.assertEqual(evidence.value_after_reader_commit, "enabled")

    def test_writer_lock_returns_busy_then_allows_retry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = pathlib.Path(temporary_directory) / DATABASE_FILENAME
            initialize_database(database_path)

            evidence = run_writer_lock(database_path)

            self.assertEqual(evidence.configured_busy_timeout_ms, BUSY_TIMEOUT_MS)
            self.assertEqual(evidence.busy_error_code, sqlite3.SQLITE_BUSY)
            self.assertEqual(evidence.committed_value_visible_during_lock, "blue")
            self.assertEqual(evidence.holder_uncommitted_value, "green-pending")
            self.assertEqual(evidence.final_committed_value, "green")
            self.assertTrue(evidence.retry_succeeded)

    def test_prepare_writes_inspectable_evidence_and_releases_database(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_dir = pathlib.Path(temporary_directory) / "state"

            evidence_path = prepare_lab(state_dir)
            payload = json.loads(evidence_path.read_text(encoding="utf-8"))

            self.assertEqual(payload["journal_mode"], "wal")
            self.assertEqual(
                payload["reader_snapshot"]["value_after_reader_commit"], "enabled"
            )
            self.assertEqual(
                payload["writer_lock"]["busy_error_code"], sqlite3.SQLITE_BUSY
            )

            # Successful removal immediately after prepare is a useful Windows
            # regression: sqlite3 context managers alone would leave files open.
            reset_generated_state(state_dir)
            self.assertFalse(state_dir.exists())

    def test_reset_preserves_learner_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_dir = pathlib.Path(temporary_directory) / "state"
            state_dir.mkdir()
            for filename in GENERATED_FILENAMES:
                (state_dir / filename).write_text("generated", encoding="utf-8")
            learner_note = state_dir / "my-observations.md"
            learner_note.write_text("keep this", encoding="utf-8")

            reset_generated_state(state_dir)

            self.assertTrue(learner_note.is_file())
            self.assertTrue(
                all(not (state_dir / name).exists() for name in GENERATED_FILENAMES)
            )


if __name__ == "__main__":
    unittest.main()
