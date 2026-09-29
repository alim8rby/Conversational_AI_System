import json
import tempfile
import unittest
from pathlib import Path

from observability.failure_store import FailureStore
from observability.failure_from_run import failures_from_run

class FailureStoreTests(unittest.TestCase):
    def test_record_list_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FailureStore(tmp)
            record = store.record(
                category="generation",
                stage="generation",
                severity="medium",
                expected_behavior="Generation succeeds.",
                actual_behavior="Generation failed.",
                evidence={"run_id": "r1"},
                session_id="s1",
            )
            self.assertEqual(store.get_failure(record["failure_id"])["status"], "open")
            summary = store.summary()
            self.assertEqual(summary["total_failures"], 1)
            self.assertEqual(summary["by_category"]["generation"], 1)

    def test_invalid_records_are_not_listed(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "bad.json").write_text(
                json.dumps({"failure_id": "bad", "status": "invalid"}),
                encoding="utf-8",
            )
            self.assertEqual(FailureStore(tmp).list_failures(), [])

    def test_run_errors_become_failure_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FailureStore(tmp)
            run = {
                "run_id": "r1",
                "timestamp_utc": "2026-01-01T00:00:00+00:00",
                "session_id": "s1",
                "metrics": {"generation": {"generation_latency_ms": 20}},
                "errors": [{"stage": "generation", "error": "provider failed"}],
            }
            failures = failures_from_run(run, store)
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0]["category"], "generation")
            self.assertEqual(failures[0]["evidence"]["run_id"], "r1")

if __name__ == "__main__":
    unittest.main()
