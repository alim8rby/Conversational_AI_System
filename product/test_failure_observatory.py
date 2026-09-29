import tempfile
import unittest

from observability.failure_store import FailureStore
from product.failure_observatory import build_failure_observatory


class FailureObservatoryTests(unittest.TestCase):
    def test_projection_contains_summary_and_failure_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FailureStore(tmp)
            record = store.record(
                category="generation",
                stage="generation",
                severity="high",
                expected_behavior="A grounded response.",
                actual_behavior="Provider failed.",
                evidence={"run_id": "r1"},
                experiment_id="EXP001",
            )
            result = build_failure_observatory(store)
            self.assertEqual(result["schema_version"], "failure-observatory-v1")
            self.assertEqual(result["summary"]["total_failures"], 1)
            self.assertEqual(result["failures"][0]["failure_id"], record["failure_id"])
            self.assertEqual(result["failures"][0]["experiment_id"], "EXP001")

    def test_filters(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FailureStore(tmp)
            store.record("generation", "generation", "high", "x", "y", {})
            store.record("voice", "voice", "low", "x", "y", {})
            result = build_failure_observatory(store, category="voice")
            self.assertEqual(len(result["failures"]), 1)
            self.assertEqual(result["failures"][0]["category"], "voice")


if __name__ == "__main__":
    unittest.main()
