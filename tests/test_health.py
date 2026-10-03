import unittest
from unittest.mock import patch

from flask import Flask

from app_health import health_response, readiness_response


class HealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)

    def test_health(self):
        with self.app.app_context():
            response, status = health_response()
        self.assertEqual(status, 200)
        self.assertEqual(response.json["status"], "ok")

    @patch("app_health.urlopen")
    @patch("app_health.load_settings")
    def test_ready(self, load_settings, urlopen):
        load_settings.return_value.ollama_base_url = "http://localhost:11434"
        with self.app.app_context():
            response, status = readiness_response()
        self.assertEqual(status, 200)
        self.assertEqual(response.json["status"], "ready")
        urlopen.assert_called_once_with("http://localhost:11434/api/tags", timeout=2)

    @patch("app_health.load_settings", side_effect=RuntimeError("missing key"))
    def test_not_ready(self, load_settings):
        with self.app.app_context():
            response, status = readiness_response()
        self.assertEqual(status, 503)
        self.assertEqual(response.json["status"], "not_ready")

    @patch("app_health.urlopen", side_effect=OSError("connection refused"))
    @patch("app_health.load_settings")
    def test_not_ready_when_ollama_unreachable(self, load_settings, urlopen):
        load_settings.return_value.ollama_base_url = "http://localhost:11434"
        with self.app.app_context():
            response, status = readiness_response()
        self.assertEqual(status, 503)
        self.assertEqual(response.json["status"], "not_ready")


if __name__ == "__main__":
    unittest.main()
