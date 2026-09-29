"""Utilities for reproducible experiment comparisons.

The runner consumes measured metric values. It never executes or invents model
results; provider-backed measurements must be supplied by an evaluation run.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def compare_metrics(baseline: dict, intervention: dict) -> dict:
    metrics = sorted(set(baseline) | set(intervention))
    comparison = {}
    for name in metrics:
        old = baseline.get(name)
        new = intervention.get(name)
        item = {"baseline": old, "intervention": new}
        if isinstance(old, (int, float)) and isinstance(new, (int, float)):
            item["delta"] = new - old
        else:
            item["delta"] = None
        comparison[name] = item
    return comparison


def evaluate_experiment(experiment: dict) -> dict:
    required = {
        "experiment_id", "title", "objective", "hypothesis", "baseline",
        "intervention", "metrics", "result", "decision", "status",
    }
    missing = sorted(required - set(experiment))
    if missing:
        raise ValueError("Missing experiment fields: " + ", ".join(missing))

    baseline = experiment["baseline"].get("measured_metrics", {})
    intervention = experiment["intervention"].get("measured_metrics", {})

    return {
        "experiment_id": experiment["experiment_id"],
        "status": experiment["status"],
        "decision": experiment["decision"],
        "metrics": compare_metrics(baseline, intervention),
        "evidence": experiment["result"].get("evidence", []),
        "measurement_complete": bool(baseline) and bool(intervention),
    }


def load_experiment(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
