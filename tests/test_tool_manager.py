import unittest

from tools.demo_ecommerce import order_lookup, product_search
from tools.tool_manager import ToolManager


class TestToolManager(unittest.TestCase):
    def test_register_and_execute(self):
        manager = ToolManager()

        manager.register("echo", lambda value: {"value": value})

        self.assertEqual(manager.tool_ids, ["echo"])
        self.assertEqual(manager.execute("echo", value="hello"), {"value": "hello"})

    def test_unknown_tool_fails(self):
        manager = ToolManager()

        with self.assertRaises(ValueError):
            manager.execute("missing")

    def test_product_search(self):
        result = product_search("TrailRunner")

        self.assertTrue(result["found"])
        self.assertEqual(result["results"][0]["product_id"], "TRX1")

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
