import unittest

from experiments.experiment_runner import compare_metrics, evaluate_experiment


class ExperimentRunnerTests(unittest.TestCase):
    def test_metric_delta(self):
        result = compare_metrics({"accuracy": 0.80}, {"accuracy": 0.90})
        self.assertEqual(result["accuracy"]["delta"], 0.10)

    def test_missing_measurement_is_not_invented(self):
        result = compare_metrics({"accuracy": 0.80}, {})
        self.assertIsNone(result["accuracy"]["delta"])

    def test_evaluation_marks_measurement_state(self):
        experiment = {
            "experiment_id": "EXP_TEST",
            "title": "Test",
            "objective": "Test comparison",
            "hypothesis": "Intervention changes accuracy",
            "baseline": {"measured_metrics": {"accuracy": 0.8}},
            "intervention": {"measured_metrics": {"accuracy": 0.9}},
            "metrics": ["accuracy"],
            "result": {"evidence": ["benchmark-run-1"]},
            "decision": "keep",
            "status": "completed",
        }
        result = evaluate_experiment(experiment)
        self.assertTrue(result["measurement_complete"])
        self.assertEqual(result["metrics"]["accuracy"]["delta"], 0.1)


if __name__ == "__main__":
    unittest.main()
