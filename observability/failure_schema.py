# Failure record validation helpers

REQUIRED_FIELDS = {"failure_id", "timestamp_utc", "category", "stage", "severity", "expected_behavior", "actual_behavior", "evidence", "status"}
CATEGORIES = {"dialogue", "retrieval", "generation", "voice", "infrastructure"}
STATUSES = {"open", "investigating", "resolved", "wont_fix"}
SEVERITIES = {"low", "medium", "high", "critical"}

def validate_failure(record):
    errors = [f"missing:{field}" for field in sorted(REQUIRED_FIELDS - record.keys())]
    if record.get("category") not in CATEGORIES: errors.append("invalid:category")
    if record.get("status") not in STATUSES: errors.append("invalid:status")
    if record.get("severity") not in SEVERITIES: errors.append("invalid:severity")
    return errors
