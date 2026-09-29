import unittest

from product.evaluation_lab import build_evaluation_lab


class EvaluationLabTests(unittest.TestCase):
    def test_lab_contract_without_runs(self):
        result = build_evaluation_lab(runs=[], retrieval_cases=None)
        self.assertEqual(result["schema_version"], "evaluation-lab-v1")
        self.assertEqual(result["evaluations"]["dialogue"]["status"], "completed")
        self.assertEqual(result["evaluations"]["integrated"]["status"], "blocked")
        self.assertEqual(result["generation"]["status"], "not_measured")

    def test_retrieval_fixture_can_be_displayed(self):
        cases = [{
            "case_id": "R1",
            "relevant_ids": ["m1"],
            "retrieved_ids": ["m1", "m2", "m3"],
            "k": 3,
        }]
        result = build_evaluation_lab(runs=[], retrieval_cases=cases)
        self.assertEqual(result["evaluations"]["retrieval"]["status"], "completed")
        self.assertEqual(result["evaluations"]["retrieval"]["metrics"]["mean_mrr"], 1.0)


if __name__ == "__main__":
    unittest.main()
