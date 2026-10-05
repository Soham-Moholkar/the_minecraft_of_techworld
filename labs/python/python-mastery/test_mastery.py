import asyncio
import tempfile
import unittest
from pathlib import Path

from mastery import (
    MemorySink,
    WorkItem,
    batches,
    enrich_all,
    normalize,
    profile_workload,
    threaded_squares,
    weighted_total,
)


class MasteryTests(unittest.TestCase):
    def test_typed_function_and_validation(self) -> None:
        self.assertEqual(normalize([1.0, 3.0]), [0.25, 0.75])
        with self.assertRaises(ValueError):
            normalize([0.0])

    def test_protocol_compatible_sink_and_generator(self) -> None:
        items = [WorkItem("a", 1.0), WorkItem("b", 2.0), WorkItem("c", 3.0)]
        sink = MemorySink()
        for batch in batches(items, 2):
            for item in batch:
                sink.write(item)
        self.assertEqual(sink.items, items)

    def test_decorator_preserves_result_and_reports_time(self) -> None:
        result, elapsed = weighted_total([WorkItem("a", 4.0)])
        self.assertEqual(result, 5.0)
        self.assertGreaterEqual(elapsed, 0.0)

    def test_async_and_threaded_work(self) -> None:
        enriched = asyncio.run(enrich_all([WorkItem("a", 2.0)]))
        self.assertEqual(enriched, [WorkItem("a", 4.0)])
        self.assertEqual(threaded_squares([2, 3, 4]), [4, 9, 16])

    def test_profiler_writes_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "profile.txt"
            report = profile_workload(destination, count=100)
            self.assertTrue(destination.exists())
            self.assertIn("weighted_total", report)


if __name__ == "__main__":
    unittest.main()
