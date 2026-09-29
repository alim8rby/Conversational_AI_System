"""Read-only failure evidence store and aggregation layer."""

import json
from collections import Counter
from pathlib import Path

from observability.failure_schema import validate_failure

class FailureStore:
    def __init__(self, failures_dir=None):
        self.failures_dir = Path(failures_dir) if failures_dir else Path(__file__).resolve().parent / "failures"

    def list_failures(self):
        records = []
        if not self.failures_dir.exists():
            return records
        for path in sorted(self.failures_dir.glob("*.json")):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                if not validate_failure(record):
                    records.append(record)
            except (OSError, json.JSONDecodeError):
                continue
        return records

    def get_failure(self, failure_id):
        path = self.failures_dir / f"{failure_id}.json"
        if not path.exists():
            return None
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return record if not validate_failure(record) else None

    def summary(self):
        failures = self.list_failures()
        by_category = Counter(f["category"] for f in failures)
        by_stage = Counter(f["stage"] for f in failures)
        by_severity = Counter(f["severity"] for f in failures)
        by_status = Counter(f["status"] for f in failures)
        return {
            "total_failures": len(failures),
            "by_category": dict(by_category),
            "by_stage": dict(by_stage),
            "by_severity": dict(by_severity),
            "by_status": dict(by_status),
        }

    def filter(self, category=None, stage=None, severity=None, status=None):
        failures = self.list_failures()
        return [
            f for f in failures
            if (category is None or f["category"] == category)
            and (stage is None or f["stage"] == stage)
            and (severity is None or f["severity"] == severity)
            and (status is None or f["status"] == status)
        ]
