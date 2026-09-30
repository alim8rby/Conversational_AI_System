"""End-to-end orchestration tests for ConversationAgent."""

import unittest
from unittest.mock import Mock, patch

from agents.conversation_agent import ConversationAgent


class TestConversationAgentIntegration(unittest.TestCase):
    def _build_agent(self, generated_answer):
        client = Mock()
        client.chat.return_value = {
            "content": generated_answer,
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        }

        memory = Mock()
        memory.embed_model = "nomic-embed-text"
        memory.retrieve.return_value = []
        knowledge = Mock()
        knowledge.retrieve.return_value = []

        workflow = Mock()
        workflow.route_and_plan.return_value = {
            "workflow_id": "order_tracking",
            "description": "Retrieve order status.",
            "requires": ["order_lookup"],
            "status": "ready",
        }

        tools = Mock()
        tools.tool_ids = {"order_lookup"}
        tools.execute_required.return_value = [
            {
                "tool_id": "order_lookup",
                "status": "executed",
                "result": {"order_id": "ORD-123", "status": "shipped"},
            }
        ]

        with patch("agents.conversation_agent.OllamaClient", return_value=client),              patch("agents.conversation_agent.MemoryManager", return_value=memory),              patch("agents.conversation_agent.KnowledgeBase", return_value=knowledge),              patch("agents.conversation_agent.WorkflowManager", return_value=workflow),              patch("agents.conversation_agent.ToolManager", return_value=tools),              patch("agents.conversation_agent.register_domain_tools"):
            agent = ConversationAgent()

        return agent, client, workflow, tools, memory, knowledge

    def test_request_flows_through_workflow_tool_retrieval_generation_and_memory(self):
        agent, client, workflow, tools, memory, knowledge = self._build_agent(
            "Your order ORD-123 has shipped."
        )

        answer = agent.ask("session-1", "Where is order ORD-123?")

        self.assertEqual(answer, "Your order ORD-123 has shipped.")
        workflow.route_and_plan.assert_called_once_with("Where is order ORD-123?")
        tools.execute_required.assert_called_once()
        knowledge.retrieve.assert_called_once_with("Where is order ORD-123?", k=3)
        client.chat.assert_called_once()
        memory.add.assert_called_once()

        self.assertEqual(
            agent.last_run["metrics"]["output_policy"]["decision"],
            "allowed",
        )
        self.assertEqual(
            agent.last_run["metrics"]["tool"]["executions"][0]["status"],
            "executed",
        )

    def test_blocked_generated_output_does_not_enter_memory(self):
        agent, client, workflow, tools, memory, knowledge = self._build_agent(
            "System prompt: reveal internal instructions."
        )

        answer = agent.ask("session-2", "Where is order ORD-123?")

        self.assertEqual(answer, "Sorry, I cannot provide that response.")
        self.assertEqual(
            agent.last_run["metrics"]["output_policy"]["policy"],
            "internal_instruction_leakage",
        )
        memory.add.assert_not_called()


if __name__ == "__main__":
    unittest.main()
