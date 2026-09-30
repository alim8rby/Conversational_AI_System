"""Tests for domain knowledge integration in ConversationAgent."""

import unittest
from unittest.mock import Mock, patch

from agents.conversation_agent import ConversationAgent


class TestKnowledgeIntegration(unittest.TestCase):
    @patch("agents.conversation_agent.MemoryManager")
    @patch("agents.conversation_agent.KnowledgeBase")
    @patch("agents.conversation_agent.OllamaClient")
    def test_agent_initializes_knowledge_components(
        self, mock_client, mock_kb, mock_memory
    ):
        agent = ConversationAgent()

        self.assertIsNotNone(agent.knowledge)
        self.assertIsNotNone(agent.context_builder)
        mock_kb.assert_called_once()

    @patch("agents.conversation_agent.MemoryManager")
    @patch("agents.conversation_agent.KnowledgeBase")
    @patch("agents.conversation_agent.OllamaClient")
    def test_knowledge_retrieval_can_be_called_independently(
        self, mock_client, mock_kb, mock_memory
    ):
        mock_kb.return_value.retrieve.return_value = [
            {
                "id": "shipping#0",
                "source": "shipping/policy.md",
                "rank": 1,
                "score": 0.9,
                "text": "Standard shipping takes 3–5 business days.",
            }
        ]

        agent = ConversationAgent()
        results = agent.knowledge.retrieve("How long is shipping?", k=3)

        self.assertEqual(results[0]["source"], "shipping/policy.md")
        self.assertEqual(results[0]["rank"], 1)


if __name__ == "__main__":
    unittest.main()
