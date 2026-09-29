import json
from pathlib import Path
from collections import Counter


class RunStore:
    """Read-only query interface for persisted run records."""

    def __init__(self, runs_dir=None):
        self.runs_dir = Path(runs_dir) if runs_dir else Path(__file__).resolve().parent / "runs"

    def list_runs(self):
        runs = []
        if not self.runs_dir.exists():
            return runs
        for path in sorted(self.runs_dir.glob("*.json")):
            try:
                runs.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                continue
        return runs

    def get_run(self, run_id):
        path = self.runs_dir / f"{run_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def summary(self):
        runs = self.list_runs()
        failed = sum(run.get("status") == "failed" for run in runs)
        successful = sum(run.get("status") == "success" for run in runs)
        return {
            "total_runs": len(runs),
            "successful_runs": successful,
            "failed_runs": failed,
            "failure_rate": failed / len(runs) if runs else 0.0,
        }


    def stage_summary(self):
        runs = self.list_runs()
        errors = []
        for run in runs:
            for error in run.get("errors", []):
                errors.append(error.get("stage", "unknown"))
        return {
            "error_count": len(errors),
            "by_stage": dict(Counter(errors)),
        }
