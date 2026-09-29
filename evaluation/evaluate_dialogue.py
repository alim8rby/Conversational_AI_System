"""Deterministic dialogue benchmark evaluator."""

import json
from pathlib import Path

from agents.conversation_agent import detect_language, is_valid_answer
from interview_manager import InterviewManager

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "evaluation" / "benchmark_v1.json"

def evaluate():
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    results = []

    manager = InterviewManager()
    section, field = manager.next_field("b001")
    ok = (section, field) == ("personal_info", "main")
    manager.record_response("b001", section, field, "I am 30 years old, work in finance, and live with my family.")
    ok = ok and manager.next_field("b001") == ("personal_info", "additional_details")
    results.append({"case_id": "B001", "status": "PASS" if ok else "FAIL"})

    ok = not is_valid_answer("k") and not is_valid_answer("ha")
    results.append({"case_id": "B002", "status": "PASS" if ok else "FAIL"})

    ok = detect_language("أنا عندي ثلاثين سنة وبشتغل في مجال المالية وبعيش مع عيلتي.") == "ar"
    results.append({"case_id": "B004", "status": "PASS" if ok else "FAIL"})

    ok = detect_language("I am 30 and work in finance.") == "en"
    results.append({"case_id": "B005", "status": "PASS" if ok else "FAIL"})

    manager = InterviewManager()
    manager.init_session("a")
    manager.init_session("b")
    manager.record_response("a", "personal_info", "main", "Only A.")
    ok = (
        manager.sessions["a"]["personal_info"]["main"] == "Only A."
        and manager.sessions["b"]["personal_info"]["main"] is None
    )
    results.append({"case_id": "B007", "status": "PASS" if ok else "FAIL"})

    manager = InterviewManager()
    manager.init_session("complete")
    for section_name in manager.sessions["complete"]:
        for field_name in manager.sessions["complete"][section_name]:
            manager.record_response("complete", section_name, field_name, "benchmark")
    ok = manager.is_complete("complete") and manager.next_field("complete") == (None, None)
    results.append({"case_id": "B008", "status": "PASS" if ok else "FAIL"})

    passed = sum(r["status"] == "PASS" for r in results)
    return {
        "benchmark_version": benchmark["benchmark_version"],
        "evaluation_type": "deterministic",
        "status": "completed",
        "cases": results,
        "metrics": {
            "deterministic_case_pass_rate": passed / len(results),
            "language_detection_accuracy": sum(
                r["status"] == "PASS" for r in results if r["case_id"] in {"B004", "B005"}
            ) / 2,
            "invalid_answer_rejection_rate": next(r["status"] == "PASS" for r in results if r["case_id"] == "B002"),
            "session_isolation_rate": next(r["status"] == "PASS" for r in results if r["case_id"] == "B007"),
            "intake_completion_success": next(r["status"] == "PASS" for r in results if r["case_id"] == "B008"),
        },
        "failures": [r["case_id"] for r in results if r["status"] == "FAIL"],
    }

if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
