"""Index a domain's declared knowledge sources into the local vector store."""

from __future__ import annotations

import argparse

from knowledge.knowledge_base import KnowledgeBase


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Index the knowledge sources declared by a domain configuration."
    )
    parser.add_argument(
        "--domain",
        default="domains/demo_ecommerce/domain.json",
        help="Path to the domain configuration JSON file.",
    )
    args = parser.parse_args()

    knowledge_base = KnowledgeBase()
    indexed = knowledge_base.index_domain_config(args.domain)

    total = sum(indexed.values())
    print(f"Indexed {total} chunks.")
    for source_id, count in indexed.items():
        print(f"  {source_id}: {count}")


if __name__ == "__main__":
    main()
