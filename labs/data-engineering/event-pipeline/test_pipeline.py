"""Recovery, replay, isolation and input-boundary regressions."""
import unittest
from pathlib import Path
from uuid import uuid4

from pipeline import Pipeline, exercise


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = Path(__file__).resolve().parent / (".test-" + uuid4().hex)
        self.directory.mkdir()
        self.path = self.directory / "pipeline.db"
        self.pipeline = Pipeline(self.path)

    def tearDown(self) -> None:
        self.pipeline.close()
        self.path.unlink()
        self.directory.rmdir()

    def test_failure_and_restart(self) -> None:
        self.pipeline.publish("atlas", "one", 7)
        with self.assertRaises(RuntimeError):
            self.pipeline.consume("atlas", "usage", fail_before_commit=True)
        self.assertEqual(self.pipeline.snapshot("atlas", "usage")["checkpoint"], 0)
        self.pipeline.close()
        self.pipeline = Pipeline(self.path)
        self.assertEqual(self.pipeline.consume("atlas", "usage")["units"], 7)
        self.assertEqual(self.pipeline.consume("atlas", "usage")["accepted"], 0)
        self.assertEqual(self.pipeline.snapshot("atlas", "usage")["units"], 7)

    def test_duplicates_and_tenants(self) -> None:
        self.assertEqual(self.pipeline.publish("atlas", "one", 2), 1)
        self.assertEqual(self.pipeline.publish("atlas", "one", 2), 1)
        with self.assertRaises(ValueError):
            self.pipeline.publish("atlas", "one", 3)
        self.pipeline.publish("other", "one", 90)
        self.assertEqual(self.pipeline.consume("atlas", "usage")["units"], 2)
        self.assertEqual(self.pipeline.snapshot("other", "usage")["lag"], 1)
        self.assertEqual(self.pipeline.consume("atlas", "report")["units"], 2)

    def test_quality_and_batch_backpressure(self) -> None:
        self.pipeline.publish("atlas", "bad", -1)
        self.pipeline.publish("atlas", "good", 8)
        result = self.pipeline.consume("atlas", "usage", 1)
        self.assertEqual((result["quarantined"], result["lag"], result["units"]), (1, 1, 0))
        result = self.pipeline.consume("atlas", "usage", 1)
        self.assertEqual((result["lag"], result["units"]), (0, 8))

    def test_invalid_inputs_do_not_mutate(self) -> None:
        for units in (True, "password", 1001):
            with self.assertRaises(ValueError):
                self.pipeline.publish("atlas", "one", units)
        for tenant in ("../escape", "x' OR 1=1--", "a" * 49):
            with self.assertRaises(ValueError):
                self.pipeline.publish(tenant, "one", 1)
        for limit in (0, 101, True):
            with self.assertRaises(ValueError):
                self.pipeline.consume("atlas", "usage", limit)
        self.assertEqual(self.pipeline.snapshot("atlas", "usage")["source_offset"], 0)

    def test_deterministic_evidence(self) -> None:
        evidence = exercise(self.path)
        self.assertTrue(evidence["crash_rolled_back"])
        self.assertEqual(evidence["recovered"]["units"], 10)
        self.assertEqual(evidence["replay"]["accepted"], 0)
        self.assertEqual(evidence["other_tenant"]["units"], 0)
