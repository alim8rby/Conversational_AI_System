"""Tests for the local knowledge vector store."""

import tempfile
import unittest

from knowledge.vector_store import LocalVectorStore


class TestLocalVectorStore(unittest.TestCase):
    def test_search_returns_matches_in_similarity_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LocalVectorStore(f"{tmp}/knowledge.json")
            store.upsert(
                [
                    {"id": "a", "source": "a.txt", "text": "low", "vector": [1.0, 0.0]},
                    {"id": "b", "source": "b.txt", "text": "high", "vector": [0.9, 0.1]},
                ]
            )

            results = store.search([1.0, 0.0], k=2)

            self.assertEqual([result["id"] for result in results], ["a", "b"])
            self.assertEqual([result["rank"] for result in results], [1, 2])
            self.assertGreater(results[0]["score"], results[1]["score"])

    def test_source_prefix_filters_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = LocalVectorStore(f"{tmp}/knowledge.json")
            store.upsert(
                [
                    {"id": "product", "source": "products/item.txt", "text": "product", "vector": [1.0, 0.0]},
                    {"id": "shipping", "source": "shipping/policy.txt", "text": "shipping", "vector": [1.0, 0.0]},
                ]
            )

            results = store.search([1.0, 0.0], k=5, source_prefix="products/")

            self.assertEqual([result["id"] for result in results], ["product"])


if __name__ == "__main__":
    unittest.main()
