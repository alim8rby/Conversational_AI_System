"""Load plain-text knowledge documents and split them into retrieval chunks."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


class DocumentLoader:
    """Load supported text documents from a domain knowledge directory."""

    SUPPORTED_SUFFIXES = {".txt", ".md"}

    def load_directory(self, path: str) -> List[Dict[str, str]]:
        root = Path(path)
        if not root.exists():
            return []

        documents: List[Dict[str, str]] = []
        for file_path in sorted(root.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in self.SUPPORTED_SUFFIXES:
                continue

            text = file_path.read_text(encoding="utf-8").strip()
            if not text:
                continue

            documents.append(
                {
                    "source": str(file_path),
                    "text": text,
                }
            )

        return documents

    def chunk(
        self,
        document: Dict[str, str],
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[Dict[str, str]]:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be >= 0 and smaller than chunk_size.")

        text = document["text"]
        if not text:
            return []

        chunks = []
        start = 0
        chunk_number = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "id": f"{document['source']}#{chunk_number}",
                        "source": document["source"],
                        "text": chunk_text,
                    }
                )

            if end == len(text):
                break

            start = end - overlap
            chunk_number += 1

        return chunks

    def load_and_chunk(
        self,
        path: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[Dict[str, str]]:
        chunks: List[Dict[str, str]] = []
        for document in self.load_directory(path):
            chunks.extend(self.chunk(document, chunk_size, overlap))
        return chunks
