"""Regression tests for correctness, plan shape, and reset discipline."""

from __future__ import annotations

import pathlib
import sqlite3
import tempfile
import unittest

from query_plan_lab import (
    COMPOSITE_INDEX,
    GENERATED_FILENAMES,
    create_and_seed,
    plan_uses_index,
    prepare_lab,
    reset_generated_state,
    run_experiment,
)


class QueryPlanExperimentTests(unittest.TestCase):
    """Prove stable invariants without asserting hardware-dependent speedups."""

    def test_index_preserves_results_and_changes_plan(self) -> None:
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("PRAGMA automatic_index = OFF")
        create_and_seed(connection, row_count=4_000)

        result = run_experiment(connection)

        self.assertEqual(result.before_rows, result.after_rows)
        self.assertGreater(len(result.after_rows), 0)
        self.assertFalse(plan_uses_index(result.before_plan, COMPOSITE_INDEX))
        self.assertTrue(plan_uses_index(result.after_plan, COMPOSITE_INDEX))

    def test_plan_evidence_is_written_for_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_dir = pathlib.Path(temporary_directory) / "state"

            evidence_path = prepare_lab(state_dir, row_count=2_000)

            self.assertTrue(evidence_path.is_file())
            self.assertTrue((state_dir / "query-plans.sqlite3").is_file())
            self.assertTrue((state_dir / "state.json").is_file())

    def test_reset_removes_generated_files_and_preserves_learner_work(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_dir = pathlib.Path(temporary_directory) / "state"
            state_dir.mkdir()
            for filename in GENERATED_FILENAMES:
                (state_dir / filename).write_text("generated", encoding="utf-8")
            learner_note = state_dir / "my-observations.md"
            learner_note.write_text("keep this", encoding="utf-8")

            reset_generated_state(state_dir)

            self.assertTrue(learner_note.is_file())
            self.assertTrue(all(not (state_dir / name).exists() for name in GENERATED_FILENAMES))

    def test_reset_removes_empty_generated_state_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_dir = pathlib.Path(temporary_directory) / "state"
            state_dir.mkdir()
            for filename in GENERATED_FILENAMES:
                (state_dir / filename).write_text("generated", encoding="utf-8")

            reset_generated_state(state_dir)

            self.assertFalse(state_dir.exists())


if __name__ == "__main__":
    unittest.main()

