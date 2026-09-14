import unittest

from agents.conversation_agent import detect_language, is_valid_answer
from interview_manager import InterviewManager


class TestConversationCore(unittest.TestCase):
    def test_language_detection(self):
        self.assertEqual(detect_language("Hello there"), "en")
        self.assertEqual(detect_language("مرحبا"), "ar")

    def test_answer_validation(self):
        self.assertFalse(is_valid_answer("ha"))
        self.assertFalse(is_valid_answer("k"))
        self.assertTrue(is_valid_answer("I feel stuck"))

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
