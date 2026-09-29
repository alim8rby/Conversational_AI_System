"""Integrated evaluation over persisted run evidence.

This module aggregates measured operational evidence only. Quality dimensions
without an executed judge remain unmeasured.
"""

import json
from pathlib import Path
from statistics import mean

from observability.run_store import RunStore

ROOT = Path(__file__).resolve().parents[1]

def evaluate_runs(runs=None):
    runs = RunStore().list_runs() if runs is None else runs
    if not runs:
        return {
            "evaluation_type": "integrated",
            "status": "blocked",
            "reason": "No persisted runs are available.",
            "metrics": {},
            "failures": [],
        }

    successful = sum(r.get("status") == "success" for r in runs)
    failed = sum(r.get("status") == "failed" for r in runs)
    latencies = [
        r["metrics"]["total_latency_ms"]
        for r in runs
        if r.get("metrics", {}).get("total_latency_ms") is not None
    ]
    voice_results = [
        r["metrics"]["voice"]["voice_success"]
        for r in runs
        if "voice_success" in r.get("metrics", {}).get("voice", {})
    ]
    token_totals = [
        r["metrics"]["generation"]["token_usage"]["total_tokens"]
        for r in runs
        if r.get("metrics", {}).get("generation", {}).get("token_usage", {}).get("total_tokens") is not None
    ]

    return {
        "evaluation_type": "integrated",
        "status": "completed",
        "run_count": len(runs),
        "metrics": {
            "run_success_rate": successful / len(runs),
            "run_failure_rate": failed / len(runs),
            "mean_total_latency_ms": mean(latencies) if latencies else None,
            "voice_success_rate": mean(voice_results) if voice_results else None,
            "mean_total_tokens": mean(token_totals) if token_totals else None,
        },
        "unmeasured": [
            "generation_quality",
            "groundedness",
            "unsupported_claims",
            "human_review",
        ],
        "failures": [
            r.get("run_id")
            for r in runs
            if r.get("status") == "failed"
        ],
    }

if __name__ == "__main__":
    print(json.dumps(evaluate_runs(), indent=2))
