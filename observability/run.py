"""Run-level observability helpers."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from observability.failure_from_run import failures_from_run

RUNS_DIR = Path(
    os.getenv(
        "OBSERVABILITY_RUNS_DIR",
        str(Path(__file__).resolve().parent / "runs"),
    )
)
STORE_INPUT = os.getenv("OBSERVABILITY_STORE_INPUT", "false").lower() == "true"


def new_run(session_id, user_message, language, metadata=None):
    return {
        "run_id": str(uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "user_message": user_message if STORE_INPUT else "[redacted]",
        "language": language,
        "status": "started",
        "metadata": metadata or {},
        "metrics": {},
        "errors": [],
        "_started_monotonic": time.perf_counter(),
    }


def finish_run(run, status="success"):
    run["status"] = status
    started = run.pop("_started_monotonic", None)
    if started is not None:
        run["metrics"]["total_latency_ms"] = round(
            (time.perf_counter() - started) * 1000, 2
        )
    persist_run(run)
    return run


def record_error(
    run,
    stage,
    error,
    *,
    severity="medium",
    expected_behavior=None,
    root_cause=None,
    experiment_id=None,
):
    run["errors"].append(
        {
            "stage": stage,
            "error": str(error),
            "severity": severity,
            "expected_behavior": expected_behavior,
            "root_cause": root_cause,
            "experiment_id": experiment_id,
            "status": "open",
        }
    )


def persist_run(run):
    """Persist a run and project its errors into FailureStore."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{run['run_id']}.json"
    path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")

    if run.get("errors"):
        failures_from_run(run)
