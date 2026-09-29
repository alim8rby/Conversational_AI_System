import unittest

from evaluation.evaluate_dialogue import evaluate
from evaluation.run_generation_eval import build_judge_record, DIMENSIONS
from evaluation.voice_evaluation import evaluate_operational_run
from evaluation.integrated_eval import evaluate_runs

class EvaluationContractTests(unittest.TestCase):
    def test_dialogue_evaluation_shape(self):
        result = evaluate()
        self.assertEqual(result["evaluation_type"], "deterministic")
        self.assertIn("metrics", result)
        self.assertIn("failures", result)

    def test_generation_judge_is_unscored_until_run(self):
        case = {"case_id": "G001"}
        record = build_judge_record(case, "sample response")
        self.assertEqual(record["status"], "pending_judgment")
        self.assertEqual(set(record["dimensions"]), set(DIMENSIONS))
        self.assertTrue(all(v["score"] is None for v in record["dimensions"].values()))

    def test_operational_metrics_do_not_invent_values(self):
        result = evaluate_operational_run({"metrics": {}})
        self.assertIsNone(result["total_latency_ms"])
        self.assertIsNone(result["voice_success"])
        self.assertEqual(result["status"], "not_measured")

    def test_integrated_evaluation_handles_missing_runs(self):
        result = evaluate_runs([])
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["metrics"], {})

if __name__ == "__main__":
    unittest.main()
