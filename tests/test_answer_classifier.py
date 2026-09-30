import unittest

from agents.answer_classifier import AnswerClassifier


class FakeOllamaClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def chat(self, messages, temperature=0.7, max_tokens=250, format=None):
        self.calls.append(
            {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "format": format,
            }
        )
        return {"content": next(self.responses)}


class TestAnswerClassifier(unittest.TestCase):
    def test_conversational_labels(self):
        cases = [
            ("What do you notice or experience in this situation?", "nothing", "en", "negative"),
            ("What brings you here today?", "لا شيء", "ar", "negative"),
            ("Tell me about yourself.", "I am just testing you", "en", "meta"),
            ("What brings you here today?", "I would rather not say", "en", "refusal"),
            (
                "Tell me about yourself.",
                "I work in finance and live with my family",
                "en",
                "answer",
            ),
            (
                "What brings you here today?",
                "The weather has been strange lately",
                "en",
                "off_topic",
            ),
            (
                "ما المشكلة الأساسية التي جعلتك تطلب المساعدة اليوم؟",
                "بجربك أشوفك هتفهم ولا لأ",
                "ar",
                "meta",
            ),
        ]

        responses = [
            '{"label":"negative","reason":"No noticeable experience is reported."}',
            '{"label":"negative","reason":"The user reports no specific concern."}',
            '{"label":"meta","reason":"The user is describing the test."}',
            '{"label":"refusal","reason":"The user declines to answer."}',
            '{"label":"answer","reason":"The user provides relevant personal information."}',
            '{"label":"off_topic","reason":"The response is unrelated to the question."}',
            '{"label":"meta","reason":"The user is describing the test."}',
        ]

        client = FakeOllamaClient(responses)
        classifier = AnswerClassifier(client)

        for question, answer, lang, expected_label in cases:
            result = classifier.classify(question, answer, lang)
            self.assertEqual(result["label"], expected_label)
            self.assertIsInstance(result["reason"], str)
            self.assertTrue(result["reason"])

    def test_classifier_requests_structured_json(self):
        client = FakeOllamaClient(
            ['{"label":"answer","reason":"Relevant response."}']
        )
        classifier = AnswerClassifier(client)

        classifier.classify(
            "Tell me about yourself.",
            "I work in finance.",
            "en",
        )

        call = client.calls[0]
        self.assertEqual(call["temperature"], 0.0)
        self.assertEqual(call["max_tokens"], 120)
        self.assertEqual(call["format"], "json")

    def test_invalid_label_raises(self):
        client = FakeOllamaClient(
            ['{"label":"maybe","reason":"Invalid label."}']
        )
        classifier = AnswerClassifier(client)

        with self.assertRaises(RuntimeError):
            classifier.classify(
                "What brings you here today?",
                "Something.",
                "en",
            )

    def test_invalid_json_raises(self):
        client = FakeOllamaClient(["not json"])
        classifier = AnswerClassifier(client)

        with self.assertRaises(RuntimeError):
            classifier.classify(
                "What brings you here today?",
                "Something.",
                "en",
            )


if __name__ == "__main__":
    unittest.main()
