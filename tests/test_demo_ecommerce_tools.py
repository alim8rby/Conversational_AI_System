"""Tests for deterministic demo e-commerce tool contracts."""

import unittest

from tools.demo_ecommerce import extract_product_query, product_search


class TestDemoEcommerceTools(unittest.TestCase):
    def test_extracts_product_name_from_natural_language(self):
        result = extract_product_query("What is the price of TrailRunner X1?")

        self.assertEqual(result, {"query": "TrailRunner X1"})

    def test_extracts_product_id(self):
        result = extract_product_query("Tell me about TRX1.")

        self.assertEqual(result, {"query": "TRX1"})

    def test_product_search_finds_extracted_product(self):
        query = extract_product_query("What is the price of TrailRunner X1?")
        result = product_search(query["query"])

        self.assertTrue(result["found"])
        self.assertEqual(result["results"][0]["product_id"], "TRX1")


if __name__ == "__main__":
    unittest.main()
