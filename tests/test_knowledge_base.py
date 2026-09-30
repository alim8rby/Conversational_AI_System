"""Tests for domain-aware knowledge base indexing."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from domains.domain_config import DomainConfig
from knowledge.knowledge_base import KnowledgeBase


class TestKnowledgeBase(unittest.TestCase):
    def test_index_domain_uses_declared_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "knowledge" / "products").mkdir(parents=True)
            (root / "knowledge" / "shipping").mkdir(parents=True)
            (root / "knowledge" / "products" / "catalog.md").write_text(
                "Product price is $10.", encoding="utf-8"
            )
            (root / "knowledge" / "shipping" / "policy.md").write_text(
                "Shipping takes three days.", encoding="utf-8"
            )
            config_path = root / "domain.json"
            config_path.write_text(
                """{
                    "domain_id": "test",
                    "name": "Test",
                    "version": "1.0",
                    "assistant": {"name": "TestBot", "purpose": "Testing"},
                    "knowledge_sources": [
                        {"id": "products", "type": "documents", "path": "knowledge/products"},
                        {"id": "shipping", "type": "documents", "path": "knowledge/shipping"}
                    ]
                }""",
                encoding="utf-8",
            )

            kb = KnowledgeBase(store_path=str(root / "vectors.json"))
            kb.client.embed = Mock(return_value=[[1.0, 0.0]])
            kb.store.upsert = Mock()

            result = kb.index_domain(DomainConfig(str(config_path)))

            self.assertEqual(result, {"products": 1, "shipping": 1})
            self.assertEqual(kb.store.upsert.call_count, 2)
            records = kb.store.upsert.call_args_list[0].args[0]
            self.assertEqual(records[0]["knowledge_source"], "products")

    def test_missing_source_is_recorded_as_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "domain.json"
            config_path.write_text(
                """{
                    "domain_id": "test",
                    "name": "Test",
                    "version": "1.0",
                    "assistant": {"name": "TestBot", "purpose": "Testing"},
                    "knowledge_sources": [
                        {"id": "missing", "type": "documents", "path": "knowledge/missing"}
                    ]
                }""",
                encoding="utf-8",
            )

            kb = KnowledgeBase(store_path=str(root / "vectors.json"))

            self.assertEqual(kb.index_domain_config(str(config_path)), {"missing": 0})


if __name__ == "__main__":
    unittest.main()
