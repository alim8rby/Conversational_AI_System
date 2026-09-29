import unittest
from unittest.mock import patch

from app_health import health_response, readiness_response


class HealthTests(unittest.TestCase):
    def test_health(self):
        response, status = health_response()
        self.assertEqual(status, 200)
        self.assertEqual(response.json["status"], "ok")

    @patch("app_health.load_settings")
    def test_ready(self, load_settings):
        response, status = readiness_response()
        self.assertEqual(status, 200)
        self.assertEqual(response.json["status"], "ready")

    @patch("app_health.load_settings", side_effect=RuntimeError("missing key"))
    def test_not_ready(self, load_settings):
        response, status = readiness_response()
        self.assertEqual(status, 503)
        self.assertEqual(response.json["status"], "not_ready")


if __name__ == "__main__":
    unittest.main()
