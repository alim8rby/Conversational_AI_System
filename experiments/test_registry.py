import unittest

from experiments.experiment_registry import load_registry, validate_experiment


class RegistryTests(unittest.TestCase):
    def test_registry_loads_valid_records(self):
        records = load_registry()
        self.assertTrue(records)
        self.assertEqual(validate_experiment(records[0]), [])

    def test_invalid_status_is_rejected(self):
        record = {
            "experiment_id": "X", "title": "X", "objective": "X",
            "hypothesis": "X", "baseline": {}, "intervention": {},
            "metrics": [], "result": {}, "decision": "keep",
            "status": "unknown",
        }
        self.assertIn("invalid:status", validate_experiment(record))


if __name__ == "__main__":
    unittest.main()
