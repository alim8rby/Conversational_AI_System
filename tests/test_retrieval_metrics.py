import unittest

from evaluation.run_retrieval_eval import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    evaluate_case,
)


class TestRetrievalMetrics(unittest.TestCase):
    def test_precision_at_k(self):
        self.assertEqual(
            precision_at_k(["m1", "m3", "m2"], {"m1", "m2"}, 3),
            2 / 3,
        )

    def test_recall_at_k(self):
        self.assertEqual(
            recall_at_k(["m1", "m3", "m2"], {"m1", "m2"}, 3),
            1.0,
        )

    def test_reciprocal_rank(self):
        self.assertEqual(
            reciprocal_rank(["m5", "m4", "m6"], {"m4"}),
            0.5,
        )

    def test_no_relevant_result(self):
        self.assertEqual(
            precision_at_k(["m1", "m2"], {"m3"}, 2),
            0.0,
        )
        self.assertEqual(
            recall_at_k(["m1", "m2"], {"m3"}, 2),
            0.0,
        )
        self.assertEqual(
            reciprocal_rank(["m1", "m2"], {"m3"}),
            0.0,
        )

    def test_evaluate_case(self):
        case = {
            "case_id": "R-test",
            "relevant_memory_ids": ["m1", "m2"],
            "retrieved_memory_ids": ["m1", "m3", "m2"],
        }

        result = evaluate_case(case, k=3)

        self.assertEqual(result["case_id"], "R-test")
        self.assertAlmostEqual(result["precision_at_k"], 2 / 3)
        self.assertEqual(result["recall_at_k"], 1.0)
        self.assertEqual(result["mrr"], 1.0)


if __name__ == "__main__":
    unittest.main()
