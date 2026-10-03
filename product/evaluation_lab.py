"""Unified read-only evaluation lab projection."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from evaluation.evaluate_dialogue import evaluate as evaluate_dialogue
from evaluation.integrated_eval import evaluate_runs
from evaluation.run_retrieval_eval import evaluate_case


ROOT = Path(__file__).resolve().parents[1]
RETRIEVAL_BENCHMARK = ROOT / "evaluation" / "retrieval_benchmark_v1.json"
GENERATION_BENCHMARK = ROOT / "evaluation" / "generation_benchmark_v1.json"


def _load_cases(path: Path) -> list[dict]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return payload.get("cases", [])


def _synthetic_retrieval_evidence() -> dict:
    cases = _load_cases(RETRIEVAL_BENCHMARK)
    evaluated = [evaluate_case(case) for case in cases]
    if not evaluated:
        return {
            "status": "blocked",
            "reason": "Retrieval benchmark fixture is unavailable or empty.",
            "metrics": {},
            "cases": [],
        }
    return {
        "status": "completed",
        "source": "synthetic-benchmark",
        "benchmark": RETRIEVAL_BENCHMARK.name,
        "cases": evaluated,
        "metrics": {
            "mean_precision_at_k": sum(c["precision_at_k"] for c in evaluated) / len(evaluated),
            "mean_recall_at_k": sum(c["recall_at_k"] for c in evaluated) / len(evaluated),
            "mean_mrr": sum(c["mrr"] for c in evaluated) / len(evaluated),
        },
    }


def _generation_evidence() -> dict:
    cases = _load_cases(GENERATION_BENCHMARK)
    return {
        "status": "not_measured",
        "source": "rubric-fixture",
        "benchmark": GENERATION_BENCHMARK.name,
        "case_count": len(cases),
        "reason": "Generation criteria are defined, but actual model outputs have not been scored.",
        "cases": [
            {
                "case_id": case.get("case_id"),
                "input": case.get("input"),
                "criteria": case.get("criteria", {}),
            }
            for case in cases
        ],
    }


def build_evaluation_lab(runs=None, retrieval_cases=None) -> dict:
    dialogue = evaluate_dialogue()
    integrated = evaluate_runs(runs)

    if retrieval_cases is not None:
        cases = [evaluate_case(case) for case in retrieval_cases]
        retrieval = {
            "evaluation_type": "retrieval",
            "status": "completed" if cases else "blocked",
            "source": "provided-fixture",
            "cases": cases,
            "metrics": {
                "mean_precision_at_k": sum(c["precision_at_k"] for c in cases) / len(cases),
                "mean_recall_at_k": sum(c["recall_at_k"] for c in cases) / len(cases),
                "mean_mrr": sum(c["mrr"] for c in cases) / len(cases),
            } if cases else {},
            "reason": None if cases else "No retrieval cases supplied.",
        }
    else:
        retrieval = {
            "evaluation_type": "retrieval",
            **_synthetic_retrieval_evidence(),
        }

    return {
        "schema_version": "evaluation-lab-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluations": {
            "dialogue": dialogue,
            "retrieval": retrieval,
            "integrated": integrated,
        },
        "generation": _generation_evidence(),
        "voice": {
            "status": "measured" if integrated.get("metrics", {}).get("voice_success_rate") is not None else "not_measured",
            "voice_success_rate": integrated.get("metrics", {}).get("voice_success_rate"),
            "reason": None if integrated.get("metrics", {}).get("voice_success_rate") is not None else "No persisted runs contain voice execution evidence.",
        },
    }
