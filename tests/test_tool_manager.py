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

    def test_prepare_and_execute_requires_input(self):
        self.manager.register(
            "lookup",
            lambda order_id: {"order_id": order_id},
            required_inputs=("order_id",),
            input_extractor=lambda text: {
                "order_id": extract_order_id(text)
            },
        )

        result = self.manager.prepare_and_execute("lookup", "check my order")

        self.assertEqual(result["status"], "requires_input")
        self.assertEqual(result["missing_inputs"], ["order_id"])

    def test_execute_required_runs_all_tools_in_order(self):
        calls = []

        self.manager.register(
            "first",
            lambda query: calls.append("first") or {"found": True},
            required_inputs=("query",),
            input_extractor=lambda text: {"query": text},
        )
        self.manager.register(
            "second",
            lambda query: calls.append("second") or {"found": True},
            required_inputs=("query",),
            input_extractor=lambda text: {"query": text},
        )

        results = self.manager.execute_required(
            ["first", "second"],
            "hello",
        )

        self.assertEqual(calls, ["first", "second"])
        self.assertEqual(
            [item["status"] for item in results],
            ["executed", "executed"],
        )

    def test_tool_exception_becomes_structured_failure(self):
        self.manager.register(
            "broken",
            lambda value: (_ for _ in ()).throw(RuntimeError("service unavailable")),
            required_inputs=("value",),
            input_extractor=lambda text: {"value": text},
        )

        result = self.manager.prepare_and_execute("broken", "hello")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["type"], "tool_execution_error")
        self.assertEqual(result["error"]["message"], "service unavailable")
        self.assertIn("latency_ms", result)

    def test_invalid_tool_output_becomes_structured_failure(self):
        self.manager.register(
            "invalid",
            lambda value: "not a dictionary",
            required_inputs=("value",),
            input_extractor=lambda text: {"value": text},
        )

        result = self.manager.prepare_and_execute("invalid", "hello")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["type"], "tool_execution_error")
        self.assertIn("dictionary", result["error"]["message"])

    def test_input_extractor_failure_becomes_structured_failure(self):
        self.manager.register(
            "bad_extractor",
            lambda value: {"value": value},
            required_inputs=("value",),
            input_extractor=lambda text: (_ for _ in ()).throw(ValueError("cannot parse input")),
        )

        result = self.manager.prepare_and_execute("bad_extractor", "hello")

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["type"], "input_extraction_error")
        self.assertEqual(result["error"]["message"], "cannot parse input")

    def test_execute_required_isolates_tool_failures(self):
        self.manager.register(
            "broken",
            lambda query: (_ for _ in ()).throw(RuntimeError("broken")),
            required_inputs=("query",),
            input_extractor=lambda text: {"query": text},
        )
        self.manager.register(
            "healthy",
            lambda query: {"ok": query},
            required_inputs=("query",),
            input_extractor=lambda text: {"query": text},
        )

        results = self.manager.execute_required(["broken", "healthy"], "hello")

        self.assertEqual(results[0]["status"], "failed")
        self.assertEqual(results[1]["status"], "executed")

    def test_timeout_policy_marks_slow_tool_as_failed(self):
        self.manager.register(
            "slow",
            lambda value: (__import__("time").sleep(0.02) or {"value": value}),
            required_inputs=("value",),
            input_extractor=lambda text: {"value": text},
        )

        result = self.manager.prepare_and_execute(
            "slow",
            "hello",
            timeout_seconds=0.001,
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["type"], "tool_timeout")
        self.assertIn("latency_ms", result)

    def test_invalid_timeout_is_structured_failure(self):
        result = self.manager.prepare_and_execute(
            "echo",
            "hello",
            timeout_seconds=0,
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["error"]["type"], "invalid_timeout")

    def test_default_timeout_is_configurable(self):
        manager = ToolManager(default_timeout_seconds=2.5)

        self.assertEqual(manager.default_timeout_seconds, 2.5)

    def test_product_search(self):
        result = product_search("TrailRunner")

        self.assertTrue(result["found"])
        self.assertEqual(result["results"][0]["product_id"], "TRX1")

    def test_product_query_extractor(self):
        from tools.demo_ecommerce import extract_product_query

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
