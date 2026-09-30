import unittest

from tools.domain_tool_registry import register_domain_tools
from tools.tool_manager import ToolManager


class TestDomainToolRegistry(unittest.TestCase):
    def test_registers_configured_tools(self):
        manager = ToolManager()

        register_domain_tools(
            manager,
            [
                {
                    "id": "product_search",
                    "handler": "tools.demo_ecommerce:product_search",
                    "input_extractor": "tools.demo_ecommerce:extract_product_query",
                    "required_inputs": ["query"],
                    "description": "Search products.",
                }
            ],
        )

        self.assertEqual(manager.tool_ids, ["product_search"])
        result = manager.prepare_and_execute(
            "product_search",
            "running shoes",
        )

        self.assertEqual(result["status"], "executed")

    def test_rejects_invalid_callable_reference(self):
        manager = ToolManager()

        with self.assertRaises(ValueError):
            register_domain_tools(
                manager,
                [
                    {
                        "id": "broken",
                        "handler": "not_a_valid_reference",
                    }
                ],
            )

    def test_rejects_missing_handler(self):
        manager = ToolManager()

        with self.assertRaises(ValueError):
            register_domain_tools(
                manager,
                [{"id": "broken"}],
            )


if __name__ == "__main__":
    unittest.main()
