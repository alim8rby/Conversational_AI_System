import unittest
from run_retrieval_eval import precision_at_k, recall_at_k, reciprocal_rank
class RetrievalMetricTests(unittest.TestCase):
    def test_precision_at_k(self): self.assertAlmostEqual(precision_at_k(["m1","m2","m3"],{"m1","m3"},3),2/3)
    def test_recall_at_k(self): self.assertAlmostEqual(recall_at_k(["m1","m2","m3"],{"m1","m3"},3),1.0)
    def test_reciprocal_rank(self): self.assertAlmostEqual(reciprocal_rank(["m9","m3","m1"],{"m1"}),1/3)
    def test_no_relevant_result(self): self.assertEqual(reciprocal_rank(["m9","m8"],{"m1"}),0.0)
if __name__=="__main__": unittest.main()
