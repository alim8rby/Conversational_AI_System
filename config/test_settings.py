import os
import unittest
from unittest.mock import patch

from config.settings import load_settings


class SettingsTests(unittest.TestCase):
    def test_ollama_configuration_is_required_for_readiness(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                load_settings(require_runtime=True)

    def test_non_runtime_config_can_load_for_unit_tests(self):
        with patch.dict(os.environ, {"PORT": "9000"}, clear=True):
            settings = load_settings(require_runtime=False)
            self.assertEqual(settings.port, 9000)
            self.assertEqual(settings.app_version, "unknown")

    def test_invalid_port_is_rejected(self):
        with patch.dict(os.environ, {"PORT": "not-a-number"}, clear=True):
            with self.assertRaises(RuntimeError):
                load_settings(require_runtime=False)


if __name__ == "__main__":
    unittest.main()
