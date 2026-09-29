"""Read-only product projection for structured failures."""

from __future__ import annotations

from observability.failure_store import FailureStore


def build_failure_observatory(store=None, category=None, stage=None, severity=None, status=None):
    store = store or FailureStore()
    failures = store.filter(category=category, stage=stage, severity=severity, status=status)
    summary = store.summary()

    return {
        "schema_version": "failure-observatory-v1",
        "summary": summary,
        "filters": {
            "category": category,
            "stage": stage,
            "severity": severity,
            "status": status,
        },
        "failures": [
            {
                "failure_id": f["failure_id"],
                "timestamp_utc": f["timestamp_utc"],
                "session_id": f.get("session_id"),
                "category": f["category"],
                "stage": f["stage"],
                "severity": f["severity"],
                "expected_behavior": f["expected_behavior"],
                "actual_behavior": f["actual_behavior"],
                "root_cause": f.get("root_cause"),
                "experiment_id": f.get("experiment_id"),
                "status": f["status"],
                "evidence": f["evidence"],
            }
            for f in failures
        ],
    }
