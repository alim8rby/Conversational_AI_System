import unittest

from interview_manager import InterviewManager
from product.session_state import build_session_state


class SessionStateTests(unittest.TestCase):
    def test_new_session_projection(self):
        manager = InterviewManager()
        state = build_session_state(manager, "s1")
        self.assertEqual(state["schema_version"], "session-state-v1")
        self.assertEqual(state["status"], "in_progress")
        self.assertEqual(state["progress"]["completed_fields"], 0)
        self.assertEqual(state["current"]["section"], "personal_info")
        self.assertEqual(state["current"]["field"], "main")

    def test_progress_updates_without_exposing_values(self):
        manager = InterviewManager()
        manager.record_response("s1", "personal_info", "main", "example")
        state = build_session_state(manager, "s1")
        self.assertEqual(state["progress"]["completed_fields"], 1)
        self.assertTrue(state["sections"][0]["fields"][0]["completed"])
        self.assertNotIn("example", str(state))

    def test_projection_isolated_by_session(self):
        manager = InterviewManager()
        manager.record_response("a", "personal_info", "main", "A")
        state_b = build_session_state(manager, "b")
        self.assertFalse(state_b["sections"][0]["fields"][0]["completed"])


if __name__ == "__main__":
    unittest.main()
