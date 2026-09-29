# Run-level observability helpers

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

RUNS_DIR = Path(__file__).resolve().parent / "runs"


def new_run(session_id, user_message, language):
    return {
        "run_id": str(uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "user_message": user_message,
        "language": language,
        "status": "started",
        "metrics": {},
        "errors": [],
    }


def finish_run(run, status="success"):
    run["status"] = status
    persist_run(run)
    return run


def record_error(run, stage, error):
    run["errors"].append({"stage": stage, "error": str(error)})


def persist_run(run):
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{run['run_id']}.json"
    path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
