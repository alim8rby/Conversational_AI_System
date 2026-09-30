"""Tests for domain knowledge document loading and chunking."""

import tempfile
import unittest
from pathlib import Path

from knowledge.document_loader import DocumentLoader


class TestDocumentLoader(unittest.TestCase):
    def test_loads_supported_text_files_and_ignores_unsupported_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shipping.md").write_text("Shipping takes 3 days.", encoding="utf-8")
            (root / "notes.txt").write_text("Returns are accepted.", encoding="utf-8")
            (root / "image.pdf").write_text("ignore me", encoding="utf-8")

            documents = DocumentLoader().load_directory(tmp)

            self.assertEqual(len(documents), 2)
            self.assertEqual(
                {Path(document["source"]).name for document in documents},
                {"shipping.md", "notes.txt"},
            )

    def test_chunks_preserve_overlap(self):
        loader = DocumentLoader()
        document = {"source": "policy.txt", "text": "abcdefghij"}

        chunks = loader.chunk(document, chunk_size=6, overlap=2)

        self.assertEqual([chunk["text"] for chunk in chunks], ["abcdef", "efghij"])


if __name__ == "__main__":
    unittest.main()
