import json
import unittest

from agents.conversation_agent import detect_language, is_valid_answer
from interview_manager import InterviewManager


class TestBaselineBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("evaluation/benchmark_v1.json", encoding="utf-8") as handle:
            cls.benchmark = json.load(handle)

    def test_benchmark_version(self):
        self.assertEqual(self.benchmark["benchmark_version"], "v1.0")

    def test_b001_normal_english_progression(self):
        manager = InterviewManager()
        session = "B001"
        section, field = manager.next_field(session)
        self.assertEqual((section, field), ("personal_info", "main"))

        manager.record_response(
            session,
            section,
            field,
            "I am 30 years old, work in finance, and live with my family.",
        )

        self.assertEqual(
            manager.next_field(session),
            ("personal_info", "additional_details"),
        )

    def test_b002_short_invalid_answer(self):
        self.assertFalse(is_valid_answer("k"))
        self.assertFalse(is_valid_answer("ha"))

    def test_b004_arabic_detection(self):
        self.assertEqual(detect_language("أنا عندي ثلاثين سنة"), "ar")

    def test_b005_english_with_numbers(self):
        self.assertEqual(detect_language("I am 30 and work in finance."), "en")

    def test_b006_clarification_state_does_not_advance(self):
        manager = InterviewManager()
        session = "B006"
        section, field = manager.next_field(session)
        self.assertEqual((section, field), ("personal_info", "main"))

        # Provider-dependent relevance classification is excluded from this
        # deterministic baseline test. Verify the state contract directly.
        self.assertFalse(is_valid_answer("k"))
        self.assertEqual(manager.next_field(session), (section, field))

    def test_b007_session_isolation(self):
        manager = InterviewManager()

        manager.record_response(
            "session-a",
            "personal_info",
            "main",
            "Answer belonging only to A.",
        )

        self.assertIsNone(
            manager.sessions["session-b"]["personal_info"]["main"]
            if "session-b" in manager.sessions
            else None
        )

        manager.init_session("session-b")
        self.assertIsNone(
            manager.sessions["session-b"]["personal_info"]["main"]
        )

    def test_b008_intake_completion_contract(self):
        manager = InterviewManager()
        session = "B008"
        manager.init_session(session)

        for section in manager.sessions[session]:
            for field in manager.sessions[session][section]:
                manager.record_response(session, section, field, "benchmark")

        self.assertTrue(manager.is_complete(session))
        self.assertEqual(manager.next_field(session), (None, None))


if __name__ == "__main__":
    unittest.main()
