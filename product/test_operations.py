import tempfile
import unittest

from observability.failure_store import FailureStore
from observability.run_store import RunStore
from product.operations import build_operations


class OperationsTests(unittest.TestCase):
    def test_operations_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            runs = RunStore(tmp + "/runs")
            failures = FailureStore(tmp + "/failures")
            result = build_operations(runs, failures)

            self.assertEqual(result["schema_version"], "operations-v1")
            self.assertIn("runs", result)
            self.assertIn("failures", result)
            self.assertIn("evaluation", result)


if __name__ == "__main__":
    unittest.main()
