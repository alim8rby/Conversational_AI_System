"""Generation evaluation helpers. Scores are never fabricated."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "evaluation" / "generation_benchmark_v1.json"
DIMENSIONS = (
    "relevance",
    "coherence",
    "instruction_adherence",
    "groundedness",
    "unsupported_claims",
)

def load_cases():
    return json.loads(BENCHMARK.read_text(encoding="utf-8"))["cases"]

def build_judge_record(case, response):
    return {
        "case_id": case["case_id"],
        "response": response,
        "dimensions": {
            dimension: {"score": None, "evidence": None}
            for dimension in DIMENSIONS
        },
        "status": "pending_judgment",
    }

def main():
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    print(json.dumps({
        "benchmark_version": benchmark["benchmark_version"],
        "evaluation_type": "generation",
        "status": "blocked",
        "reason": "Actual model responses and a declared judge or human review are required. No scores are fabricated.",
        "dimensions": list(DIMENSIONS),
        "cases": [case["case_id"] for case in benchmark["cases"]],
    }, indent=2))

if __name__ == "__main__":
    main()
