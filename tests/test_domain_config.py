import unittest

from domains.domain_config import DomainConfig


class TestDomainConfig(unittest.TestCase):
    def test_demo_domain_loads(self):
        domain = DomainConfig("domains/demo_ecommerce/domain.json")

        self.assertEqual(domain.domain_id, "demo_ecommerce")
        self.assertEqual(domain.name, "Demo E-commerce Assistant")
        self.assertEqual(domain.assistant["name"], "ShopAssist")
        self.assertFalse(domain.intake_enabled)
        self.assertTrue(domain.knowledge_sources)
        self.assertIn("order_tracking", domain.workflows)
        self.assertIn("order_lookup", [tool["id"] for tool in domain.tools])
        self.assertTrue(domain.policies)

    def test_missing_file_fails_clearly(self):
        with self.assertRaises(FileNotFoundError):
            DomainConfig("domains/does_not_exist/domain.json")

    def test_missing_required_field_fails_validation(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "domain.json"
            path.write_text(
                '{"domain_id": "broken", "name": "Broken", "version": "1.0"}',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                DomainConfig(str(path))


if __name__ == "__main__":
    unittest.main()
