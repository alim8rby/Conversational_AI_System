import json
import tempfile
import unittest
from pathlib import Path

from observability.run_store import RunStore


class RunStoreTests(unittest.TestCase):
    def test_lists_and_reads_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run-1.json"
            path.write_text(json.dumps({"run_id": "run-1", "status": "success"}), encoding="utf-8")

            store = RunStore(tmp)

            self.assertEqual(store.list_runs()[0]["run_id"], "run-1")
            self.assertEqual(store.get_run("run-1")["status"], "success")

    def test_summary_counts_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.json").write_text(json.dumps({"run_id": "a", "status": "success"}), encoding="utf-8")
            Path(tmp, "b.json").write_text(json.dumps({"run_id": "b", "status": "failed"}), encoding="utf-8")

            summary = RunStore(tmp).summary()

            self.assertEqual(summary["total_runs"], 2)
            self.assertEqual(summary["successful_runs"], 1)
            self.assertEqual(summary["failed_runs"], 1)
            self.assertEqual(summary["failure_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
