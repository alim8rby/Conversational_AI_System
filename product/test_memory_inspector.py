import unittest

from product.memory_inspector import inspect_memory


class FakeManager:
    def retrieve(self, session_id, query, k=3):
        return [
            {"memory_id": "m1", "rank": 1, "score": 0.91, "text": "Earlier context"},
            {"memory_id": "m2", "rank": 2, "score": 0.72, "text": "Another context"},
        ][:k]


class MemoryInspectorTests(unittest.TestCase):
    def test_projection_contract(self):
        result = inspect_memory(FakeManager(), "s1", "work stress", 2)
        self.assertEqual(result["schema_version"], "memory-inspector-v1")
        self.assertEqual(result["retrieved_count"], 2)
        self.assertEqual(result["memories"][0]["memory_id"], "m1")
        self.assertEqual(result["memories"][0]["rank"], 1)
        self.assertEqual(result["memories"][0]["score"], 0.91)

    def test_invalid_k_rejected(self):
        with self.assertRaises(ValueError):
            inspect_memory(FakeManager(), "s1", "query", 0)

    def test_no_vector_values_exposed(self):
        result = inspect_memory(FakeManager(), "s1", "query")
        self.assertNotIn("values", str(result))


if __name__ == "__main__":
    unittest.main()
