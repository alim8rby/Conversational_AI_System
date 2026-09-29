"""Validation and discovery helpers for experiment records."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_FIELDS = {
    "experiment_id", "title", "objective", "hypothesis", "baseline",
    "intervention", "metrics", "result", "decision", "status",
}
STATUSES = {"planned", "running", "completed", "blocked"}
DECISIONS = {"keep", "revert", "iterate", "inconclusive"}


def validate_experiment(record):
    errors = [f"missing:{field}" for field in sorted(REQUIRED_FIELDS - record.keys())]
    if record.get("status") not in STATUSES:
        errors.append("invalid:status")
    if record.get("decision") not in DECISIONS:
        errors.append("invalid:decision")
    if not isinstance(record.get("metrics"), list):
        errors.append("invalid:metrics")
    return errors


def load_registry(registry_path=None):
    path = Path(registry_path) if registry_path else Path(__file__).resolve().parent / "registry.json"
    if not path.exists():
        return []
    records = json.loads(path.read_text(encoding="utf-8"))
    return [record for record in records if not validate_experiment(record)]
