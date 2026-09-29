"""Convert persisted run evidence into structured failure records."""

from observability.failure_store import FailureStore

def failures_from_run(run, store=None):
    store = store or FailureStore()
    created = []

    for error in run.get("errors", []):
        stage = error.get("stage", "unknown")
        category = {
            "generation": "generation",
            "voice": "voice",
            "retrieval": "retrieval",
            "classification": "dialogue",
            "application": "infrastructure",
        }.get(stage, "infrastructure")

        created.append(store.record(
            category=category,
            stage=stage,
            severity="medium",
            expected_behavior="Run stage completes without an error.",
            actual_behavior=error.get("error", "Unknown error"),
            evidence={
                "run_id": run.get("run_id"),
                "timestamp_utc": run.get("timestamp_utc"),
                "metrics": run.get("metrics", {}).get(stage, {}),
            },
            session_id=run.get("session_id"),
            status="open",
        ))

    return created
