import json
import unittest

from domains.domain_config import DomainConfig
from workflows.workflow_manager import WorkflowManager


class FakeClient:
    def __init__(self, workflow_id="product_question"):
        self.workflow_id = workflow_id

    def chat(self, messages, temperature=0.0, max_tokens=120, format="json"):
        return {
            "content": json.dumps(
                {
                    "workflow_id": self.workflow_id,
                    "reason": "The request matches the configured workflow.",
                }
            )
        }


class TestWorkflowManager(unittest.TestCase):
    def setUp(self):
        self.domain = DomainConfig("domains/demo_ecommerce/domain.json")

    def test_normalizes_string_workflows(self):
        manager = WorkflowManager(self.domain, FakeClient())
        self.assertIn("product_question", manager.workflow_ids)

    def test_routes_and_builds_plan(self):
        manager = WorkflowManager(self.domain, FakeClient())
        plan = manager.route_and_plan("Tell me about the TrailRunner X1.")

        self.assertEqual(plan["workflow_id"], "product_question")
        self.assertEqual(plan["status"], "ready")
        self.assertIn("requires", plan)

    def test_rejects_unknown_workflow(self):
        manager = WorkflowManager(self.domain, FakeClient())
        with self.assertRaises(ValueError):
            manager.build_plan("does_not_exist")


if __name__ == "__main__":
    unittest.main()
