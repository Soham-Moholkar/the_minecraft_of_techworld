import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from failure_modes import (
    build_zipapp,
    measure_generator_memory,
    parallel_squares_resilient,
)
from mastery import WorkItem, batches, normalize


class AdvancedMasteryTests(unittest.TestCase):
    def test_randomized_normalization_invariants(self) -> None:
        """Seeded trials provide repeatable property-style evidence offline."""

        # Deterministic pseudo-randomness is intentional for a repeatable test corpus.
        generator = random.Random(20260827)  # noqa: S311
        for _ in range(100):
            sample_size = generator.randint(1, 30)
            values = [generator.uniform(0.01, 100.0) for _ in range(sample_size)]
            normalized = normalize(values)
            self.assertAlmostEqual(sum(normalized), 1.0)
            self.assertEqual(len(normalized), len(values))
            self.assertTrue(all(value > 0 for value in normalized))

    def test_randomized_batches_are_lossless(self) -> None:
        generator = random.Random(42)  # noqa: S311 - reproducible test data
        for count in range(1, 40):
            items = [WorkItem(str(index), generator.random()) for index in range(count)]
            size = generator.randint(1, 8)
            reconstructed = [item for batch in batches(items, size) for item in batch]
            self.assertEqual(reconstructed, items)

    def test_process_pool_isolates_item_failure(self) -> None:
        result = parallel_squares_resilient([2, -1, 3])
        self.assertEqual(result.succeeded, {2: 4, 3: 9})
        self.assertEqual(result.failed, {-1: "negative work item"})

    def test_generator_memory_evidence_is_bounded_and_correct(self) -> None:
        evidence = measure_generator_memory(1_000)
        self.assertEqual(evidence.total, sum(value * value for value in range(1_000)))
        self.assertEqual(evidence.item_count, 1_000)
        self.assertGreater(evidence.peak_bytes, 0)
        self.assertLess(evidence.peak_bytes, 1_000_000)

    def test_zipapp_is_executable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            archive = build_zipapp(Path(directory) / "python-mastery.pyz")
            result = subprocess.run(  # noqa: S603 - fixed interpreter and generated local archive
                [sys.executable, str(archive)],
                check=True,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.stdout.strip(), "atlas-python-mastery total=10.00")


if __name__ == "__main__":
    unittest.main()
