"""Convert run errors into structured FailureStore records."""

from __future__ import annotations

from observability.failure_store import FailureStore


STAGE_CATEGORIES = {
    "generation": "generation",
    "voice": "voice",
    "retrieval": "retrieval",
    "classification": "dialogue",
    "application": "infrastructure",
    "tool": "tool",
    "workflow": "dialogue",
}


def failures_from_run(run, store=None):
    """Persist every recorded run error as a failure record."""
    store = store or FailureStore()
    created = []

    for error in run.get("errors", []):
        stage = error.get("stage", "unknown")
        created.append(
            store.record(
                category=STAGE_CATEGORIES.get(stage, "infrastructure"),
                stage=stage,
                severity=error.get("severity", "medium"),
                expected_behavior=error.get(
                    "expected_behavior", "Run stage completes without an error."
                ),
                actual_behavior=error.get("error", "Unknown error"),
                evidence={
                    "run_id": run.get("run_id"),
                    "timestamp_utc": run.get("timestamp_utc"),
                    "metrics": run.get("metrics", {}).get(stage, {}),
                    "metadata": run.get("metadata", {}),
                },
                session_id=run.get("session_id"),
                root_cause=error.get("root_cause"),
                experiment_id=error.get("experiment_id"),
                status=error.get("status", "open"),
            )
        )

    return created
