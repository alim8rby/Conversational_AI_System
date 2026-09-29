import inspect
import unittest

from agents.conversation_agent import detect_language, is_valid_answer
from interview_manager import InterviewManager
from memory.memory_manager import MemoryManager


class TestConversationCore(unittest.TestCase):
    def test_language_detection(self):
        self.assertEqual(detect_language("Hello there"), "en")
        self.assertEqual(detect_language("مرحبا"), "ar")

    def test_answer_validation(self):
        self.assertFalse(is_valid_answer("ha"))
        self.assertFalse(is_valid_answer("k"))
        self.assertTrue(is_valid_answer("I feel stuck"))

    def test_language_detection_with_numbers(self):
        self.assertEqual(detect_language("I am 30 years old."), "en")
        self.assertEqual(detect_language("أنا عندي 30 سنة"), "ar")

    def test_retrieval_result_contract(self):
        self.assertTrue("List[Dict]" in "import os\\nfrom typing import Dict, List\\n\\nfrom pinecone import Pinecone\\nfrom together import Together\\n\\n\\nclass MemoryManager:\\n    \\"\\"\\"Session-scoped semantic memory backed by Pinecone.\\"\\"\\"\\n\\n    def __init__(self, embed_model: str, index_name: str):\\n        together_api_key = os.getenv(\\"TOGETHER_API_KEY\\")\\n        pinecone_api_key = os.getenv(\\"PINECONE_API_KEY\\")\\n        if not together_api_key:\\n            raise RuntimeError(\\"TOGETHER_API_KEY is not set\\")\\n        if not pinecone_api_key:\\n            raise RuntimeError(\\"PINECONE_API_KEY is not set\\")\\n        self.client = Together(api_key=together_api_key)\\n        self.pinecone = Pinecone(api_key=pinecone_api_key)\\n        self.index = self.pinecone.Index(index_name)\\n        self.embed_model = embed_model\\n\\n    def _embed(self, text: str) -> List[float]:\\n        response = self.client.embeddings.create(model=self.embed_model, input=text)\\n        return response.data[0].embedding\\n\\n    def add(self, session_id: str, key: str, text: str) -> None:\\n        vector = self._embed(text)\\n        self.index.upsert(vectors=[{\\n            \\"id\\": key,\\n            \\"values\\": vector,\\n            \\"metadata\\": {\\"session\\": session_id, \\"text\\": text},\\n        }])\\n\\n    def retrieve(self, session_id: str, query: str, k: int = 3) -> List[Dict]:\\n        qvec = self._embed(query)\\n        results = self.index.query(\\n            vector=qvec,\\n            top_k=k,\\n            include_values=False,\\n            include_metadata=True,\\n            filter={\\"session\\": {\\"$eq\\": session_id}},\\n        )\\n        return [\\n            {\\n                \\"text\\": match.metadata[\\"text\\"],\\n                \\"score\\": match.score,\\n                \\"rank\\": rank,\\n                \\"memory_id\\": match.id,\\n            }\\n            for rank, match in enumerate(results.matches, start=1)\\n            if match.metadata and match.metadata.get(\\"text\\")\\n        ]\\n")

    def test_interview_progression(self):
        manager = InterviewManager()
        session = "test-session"
        section, field = manager.next_field(session)
        self.assertEqual((section, field), ("personal_info", "main"))
        manager.record_response(session, section, field, "I work in technology and live in Cairo.")
        self.assertEqual(manager.next_field(session), ("personal_info", "additional_details"))

    def test_flat_sheet(self):
        manager = InterviewManager()
        session = "sheet-test"
        manager.record_response(session, "personal_info", "main", "I am 30 years old.")
        self.assertIn("Personal Info [main]: I am 30 years old.", manager.get_flat_sheet(session))

    def test_run_record_contract(self):
        from observability.run import finish_run, new_run, record_error

        run = new_run(
            "session-1",
            "I am 30 years old.",
            "en",
            metadata={
                "application_version": "test",
                "model": "test-model",
                "embedding_model": "test-embed",
                "pinecone_index": "test-index",
                "prompt_version": "v1",
                "retrieval_k": 3,
                "temperature": 0.7,
                "max_tokens": 250,
            },
        )
        self.assertTrue(run["run_id"])
        self.assertEqual(run["session_id"], "session-1")
        self.assertEqual(run["language"], "en")
        self.assertEqual(run["status"], "started")
        self.assertEqual(run["errors"], [])
        self.assertEqual(run["metadata"]["model"], "test-model")
        run["metrics"]["dialogue"] = {"input_valid": True}
        record_error(run, "test", "example")
        finish_run(run, "failed")
        self.assertEqual(run["status"], "failed")
        self.assertEqual(run["errors"][0]["stage"], "test")
        self.assertIn("total_latency_ms", run["metrics"])


if __name__ == "__main__":
    unittest.main()
