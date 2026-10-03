import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from memory.memory_manager import MemoryManager


class TestMemoryManager(unittest.TestCase):
    def _build_manager(self, embeddings):
        client = Mock()
        client.embed.side_effect = embeddings

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        store_path = Path(temp_dir.name) / "memory.json"

        with patch("memory.memory_manager.OllamaClient", return_value=client):
            manager = MemoryManager(
                embed_model="nomic-embed-text",
                store_path=str(store_path),
            )

        return manager, client, store_path

    def test_retrieval_is_scoped_to_session(self):
        manager, client, store_path = self._build_manager(
            [
                [[1.0, 0.0]],
                [[1.0, 0.0]],
                [[1.0, 0.0]],
            ]
        )

        manager.add("session-a", "memory-a", "User likes Python.")
        manager.add("session-b", "memory-b", "User likes Python.")

        results = manager.retrieve(
            "session-a",
            "What programming language does the user like?",
            k=3,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["memory_id"], "memory-a")
        self.assertEqual(results[0]["text"], "User likes Python.")

    def test_retrieval_returns_ranked_semantic_matches(self):
        manager, client, store_path = self._build_manager(
            [
                [[1.0, 0.0]],
                [[0.8, 0.6]],
                [[0.0, 1.0]],
                [[0.9, 0.1]],
            ]
        )

        manager.add("session-a", "memory-1", "User likes Python.")
        manager.add("session-a", "memory-2", "User likes hiking.")
        manager.add("session-a", "memory-3", "User likes cooking.")

        results = manager.retrieve(
            "session-a",
            "What programming language does the user like?",
            k=2,
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["memory_id"], "memory-1")
        self.assertEqual(results[0]["rank"], 1)
        self.assertEqual(results[1]["rank"], 2)
        self.assertGreaterEqual(results[0]["score"], results[1]["score"])

    def test_memory_store_persists_records_as_json(self):
        manager, client, store_path = self._build_manager(
            [
                [[1.0, 0.0]],
            ]
        )

        manager.add("session-a", "memory-a", "User likes Python.")

        records = json.loads(store_path.read_text(encoding="utf-8"))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], "memory-a")
        self.assertEqual(records[0]["session"], "session-a")
        self.assertEqual(records[0]["text"], "User likes Python.")
        self.assertEqual(records[0]["vector"], [1.0, 0.0])


if __name__ == "__main__":
    unittest.main()
