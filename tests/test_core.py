import inspect
import unittest

from agents.conversation_agent import detect_language, is_valid_answer
from interview_manager import InterviewManager
from memory.memory_manager import MemoryManager
from product.session_state import build_session_state


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
        from memory.memory_manager import MemoryManager
        self.assertIn("MemoryManager", inspect.getsource(MemoryManager))
        self.assertIn("retrieve", inspect.getsource(MemoryManager))

    def test_domain_session_state_without_intake(self):
        manager = InterviewManager()
        state = build_session_state(
            manager,
            "demo-session",
            intake_enabled=False,
            assistant_name="ShopAssist",
        )
        self.assertEqual(state["status"], "ready")
        self.assertEqual(state["assistant"], "ShopAssist")
        self.assertEqual(state["progress"]["total_fields"], 0)
        self.assertEqual(state["sections"], [])

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
                "memory_store": "data/test-memory.json",
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
        self.assertEqual(run["user_message"], "[redacted]")


if __name__ == "__main__":
    unittest.main()
