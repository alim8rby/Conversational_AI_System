import unittest

from tools.demo_ecommerce import (
    extract_order_id,
    extract_product_query,
    order_lookup,
    product_search,
)
from tools.tool_manager import ToolManager


class TestToolManager(unittest.TestCase):
    def setUp(self):
        self.manager = ToolManager()
        self.manager.register(
            "echo",
            lambda value: {"value": value},
            required_inputs=("value",),
        )

    def test_register_and_execute(self):
        self.assertEqual(self.manager.tool_ids, ["echo"])
        self.assertEqual(self.manager.execute("echo", value="hello"), {"value": "hello"})

    def test_unknown_tool_fails(self):
        with self.assertRaises(ValueError):
            self.manager.execute("missing")

    def test_missing_required_input_fails(self):
        with self.assertRaises(ValueError):
            self.manager.execute("echo")

    def test_prepare_inputs(self):
        self.manager.register(
            "lookup",
            lambda order_id: {"order_id": order_id},
            required_inputs=("order_id",),
            input_extractor=lambda text: {
                "order_id": extract_order_id(text)
            },
        )

        self.assertEqual(
            self.manager.prepare_inputs("lookup", "check demo-1001"),
            {"order_id": "DEMO-1001"},
        )

    def test_missing_inputs(self):
        self.assertEqual(
            self.manager.missing_inputs("echo", {}),
            ["value"],
        )

    def test_product_search(self):
        result = product_search("TrailRunner")

        self.assertTrue(result["found"])
        self.assertEqual(result["results"][0]["product_id"], "TRX1")

    def test_product_query_extractor(self):
        self.assertEqual(
            extract_product_query("Do you have running shoes?"),
            {"query": "Do you have running shoes?"},
        )

    def test_order_lookup(self):
        result = order_lookup("demo-1001")

        self.assertTrue(result["found"])
        self.assertEqual(result["status"], "shipped")

    def test_unknown_order_does_not_invent_status(self):
        result = order_lookup("DEMO-9999")

        self.assertFalse(result["found"])
        self.assertNotIn("status", result)


if __name__ == "__main__":
    unittest.main()
