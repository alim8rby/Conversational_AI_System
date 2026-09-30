"""Tests for controlled knowledge context construction."""

import unittest

from knowledge.context_builder import KnowledgeContextBuilder


class TestKnowledgeContextBuilder(unittest.TestCase):
    def test_build_preserves_traceability_and_order(self):
        results = [
            {
                "id": "shipping#0",
                "source": "shipping/policy.md",
                "rank": 1,
                "score": 0.91,
                "text": "Ships within three business days.",
            },
            {
                "id": "returns#0",
                "source": "returns/policy.md",
                "rank": 2,
                "score": 0.84,
                "text": "Returns are accepted within thirty days.",
            },
        ]

        payload = KnowledgeContextBuilder().build(results)

        self.assertEqual(payload["retrieved_count"], 2)
        self.assertEqual(payload["included_count"], 2)
        self.assertEqual(payload["sources"][0]["source"], "shipping/policy.md")
        self.assertIn("[Source 1]", payload["context"])
        self.assertIn("[Source 2]", payload["context"])

    def test_context_is_bounded(self):
        results = [
            {
                "id": "a",
                "source": "a.md",
                "rank": 1,
                "score": 0.9,
                "text": "abcdefghij",
            },
            {
                "id": "b",
                "source": "b.md",
                "rank": 2,
                "score": 0.8,
                "text": "klmnopqrst",
            },
        ]

        payload = KnowledgeContextBuilder().build(results, max_chars=12)

        self.assertEqual(payload["context_chars"], 12)
        self.assertEqual(payload["included_count"], 2)
        self.assertTrue(payload["sources"][1]["truncated"])

    def test_invalid_limit_fails(self):
        with self.assertRaises(ValueError):
            KnowledgeContextBuilder().build([], max_chars=0)


if __name__ == "__main__":
    unittest.main()
