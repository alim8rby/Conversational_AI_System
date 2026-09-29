"""Read-only operator dashboard projection."""

from __future__ import annotations

from observability.run_store import RunStore
from observability.failure_store import FailureStore
from product.evaluation_lab import build_evaluation_lab


def build_operations(store=None, failures=None):
    run_store = store or RunStore()
    failure_store = failures or FailureStore()
    run_summary = run_store.summary()
    stage_summary = run_store.stage_summary()
    failure_summary = failure_store.summary()
    evaluation = build_evaluation_lab()

    integrated = evaluation["evaluations"]["integrated"]
    metrics = integrated.get("metrics", {})

    return {
        "schema_version": "operations-v1",
        "system": {
            "health": "unknown",
            "readiness": "unknown",
            "note": "Health/readiness are exposed by dedicated endpoints.",
        },
        "runs": {
            **run_summary,
            **stage_summary,
            "mean_total_latency_ms": metrics.get("mean_total_latency_ms"),
        },
        "failures": failure_summary,
        "evaluation": {
            "dialogue_status": evaluation["evaluations"]["dialogue"].get("status"),
            "retrieval_status": evaluation["evaluations"]["retrieval"].get("status"),
            "generation_status": evaluation["generation"].get("status"),
            "voice_status": evaluation["voice"].get("status"),
            "run_success_rate": metrics.get("run_success_rate"),
        },
    }
