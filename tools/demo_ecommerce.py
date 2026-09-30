"""Deterministic demo e-commerce tools.

These tools intentionally use local demo data. They provide a real execution
boundary for the architecture without pretending to access a live store.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List


PRODUCTS = [
    {
        "product_id": "TRX1",
        "name": "TrailRunner X1",
        "category": "Running shoes",
        "price": 89,
        "sizes": ["US 7", "US 8", "US 9", "US 10", "US 11", "US 12"],
        "colors": ["Black", "blue"],
    },
    {
        "product_id": "UP20",
        "name": "UrbanPack 20",
        "category": "Backpacks",
        "price": 54,
        "sizes": [],
        "colors": ["Black", "gray"],
    },
    {
        "product_id": "SM01",
        "name": "SoundMini",
        "category": "Wireless headphones",
        "price": 39,
        "sizes": [],
        "colors": ["Black", "white"],
    },
]

ORDERS = {
    "DEMO-1001": {
        "status": "shipped",
        "carrier": "Demo Express",
        "estimated_delivery": "2026-10-02",
    },
    "DEMO-1002": {
        "status": "processing",
        "carrier": None,
        "estimated_delivery": None,
    },
}


def extract_order_id(text: str) -> str | None:
    """Extract a demo order ID from natural-language user input."""
    match = re.search(r"\bDEMO-\d{4}\b", text.upper())
    return match.group(0) if match else None


def product_search(query: str) -> Dict[str, Any]:
    """Search the static demo catalog by name, category, or product ID."""
    normalized = query.strip().lower()
    if not normalized:
        return {"found": False, "results": [], "source": "demo_catalog"}

    results: List[Dict[str, Any]] = []
    for product in PRODUCTS:
        searchable = " ".join(
            [
                product["product_id"],
                product["name"],
                product["category"],
                *product["colors"],
            ]
        ).lower()
        if normalized in searchable:
            results.append(product)

    return {
        "found": bool(results),
        "results": results,
        "source": "demo_catalog",
    }


def order_lookup(order_id: str) -> Dict[str, Any]:
    """Look up a known demo order without claiming live-store access."""
    normalized = order_id.strip().upper()
    order = ORDERS.get(normalized)

    if order is None:
        return {
            "found": False,
            "order_id": normalized,
            "source": "demo_order_system",
        }

    return {
        "found": True,
        "order_id": normalized,
        **order,
        "source": "demo_order_system",
    }


def extract_product_query(text: str) -> Dict[str, Any]:
    """Extract a catalog identifier or known product name from a user request."""
    normalized = text.strip()
    upper_text = normalized.upper()

    for product in PRODUCTS:
        product_id = product["product_id"]
        if product_id in upper_text:
            return {"query": product_id}

        product_name = product["name"]
        if product_name.lower() in normalized.lower():
            return {"query": product_name}

    return {"query": normalized}
