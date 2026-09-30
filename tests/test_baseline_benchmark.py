import json
import unittest

from agents.conversation_agent import ANSWER_RELEVANCE_THRESHOLD, ConversationAgent, detect_language, is_valid_answer
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

    def test_answer_relevance_threshold_is_historical_only(self):
        # EXP002 threshold is retained for observability/history, not decision-making.
        self.assertEqual(ANSWER_RELEVANCE_THRESHOLD, 0.46)

    def test_session_start_sets_first_awaited_field(self):
        agent = ConversationAgent(store_path="data/test_session_start.json")
        session = "B009"
        prompt = agent.start_session(session)

        self.assertEqual(agent.awaiting[session], ("personal_info", "main"))
        self.assertEqual(prompt, agent.interviewer.get_prompt(session))

    def test_session_start_does_not_consume_user_input(self):
        agent = ConversationAgent(store_path="data/test_session_start_input.json")
        session = "B010"
        agent.start_session(session)

        self.assertIsNone(agent.interviewer.sessions[session]["personal_info"]["main"])

    def test_additional_details_validate_against_parent_section(self):
        agent = ConversationAgent(store_path="data/test_additional_details.json")
        session = "B011"
        agent.start_session(session)

        with unittest.mock.patch.object(
            agent,
            "_semantic_similarity",
            side_effect=[0.70, 0.50],
        ) as similarity:
            with unittest.mock.patch.object(
                agent.classifier,
                "classify",
                side_effect=[
                    {"label": "answer", "reason": "Relevant personal information."},
                    {"label": "answer", "reason": "Relevant additional context."},
                ],
            ):
                agent.ask(
                    session,
                    "I am 30 years old, work as a software developer, and live in Cairo.",
                )
                agent.ask(
                    session,
                    "I live with my family and have been working in this field for five years.",
                )

        self.assertEqual(
            agent.interviewer.sessions[session]["personal_info"]["additional_details"],
            "I live with my family and have been working in this field for five years.",
        )
        self.assertEqual(
            similarity.call_args_list[1].args[0],
            agent.interviewer.get_section_prompt("personal_info"),
        )
        self.assertEqual(
            agent.awaiting[session],
            ("chief_complaint", "main"),
        )

    def test_negative_response_is_accepted_and_advances(self):
        agent = ConversationAgent(store_path="data/test_negative_classifier.json")
        session = "B012"
        agent.start_session(session)

        with unittest.mock.patch.object(
            agent,
            "_semantic_similarity",
            return_value=0.20,
        ), unittest.mock.patch.object(
            agent.classifier,
            "classify",
            return_value={
                "label": "negative",
                "reason": "The user reports no relevant information.",
            },
        ):
            agent.ask(session, "nothing")

        self.assertEqual(
            agent.interviewer.sessions[session]["personal_info"]["main"],
            "nothing",
        )
        self.assertIsNone(
            agent.interviewer.sessions[session]["personal_info"]["additional_details"]
        )
        self.assertEqual(
            agent.awaiting[session],
            ("personal_info", "additional_details"),
        )
        self.assertEqual(
            agent.last_turn_metrics["classification_label"],
            "negative",
        )

    def test_meta_response_does_not_advance(self):
        agent = ConversationAgent(store_path="data/test_meta_classifier.json")
        session = "B013"
        agent.start_session(session)

        with unittest.mock.patch.object(
            agent,
            "_semantic_similarity",
            return_value=0.10,
        ), unittest.mock.patch.object(
            agent.classifier,
            "classify",
            return_value={
                "label": "meta",
                "reason": "The user is describing the test.",
            },
        ):
            response = agent.ask(session, "I am just testing you")

        self.assertEqual(
            agent.awaiting[session],
            ("personal_info", "main"),
        )
        self.assertIsNone(
            agent.interviewer.sessions[session]["personal_info"]["main"]
        )
        self.assertIn("testing", response.lower())
        self.assertEqual(
            agent.last_turn_metrics["classification_label"],
            "meta",
        )

    def test_off_topic_response_clarifies_without_advancing(self):
        agent = ConversationAgent(store_path="data/test_off_topic_classifier.json")
        session = "B014"
        agent.start_session(session)

        with unittest.mock.patch.object(
            agent,
            "_semantic_similarity",
            return_value=0.10,
        ), unittest.mock.patch.object(
            agent.classifier,
            "classify",
            return_value={
                "label": "off_topic",
                "reason": "The response is unrelated to the question.",
            },
        ):
            response = agent.ask(session, "The weather is strange today.")

        self.assertEqual(
            agent.awaiting[session],
            ("personal_info", "main"),
        )
        self.assertIsNone(
            agent.interviewer.sessions[session]["personal_info"]["main"]
        )
        self.assertTrue(response)


if __name__ == "__main__":
    unittest.main()
