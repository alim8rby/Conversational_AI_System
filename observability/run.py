# Run-level observability helpers

from datetime import datetime, timezone
from uuid import uuid4


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
    return run


def record_error(run, stage, error):
    run["errors"].append({"stage": stage, "error": str(error)})
