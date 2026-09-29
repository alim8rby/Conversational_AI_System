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


if __name__ == "__main__":
    unittest.main()
