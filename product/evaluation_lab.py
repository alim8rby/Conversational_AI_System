"""Unified read-only evaluation lab projection."""

from __future__ import annotations

from datetime import datetime, timezone

from evaluation.evaluate_dialogue import evaluate as evaluate_dialogue
from evaluation.integrated_eval import evaluate_runs
from evaluation.run_retrieval_eval import evaluate_case


def build_evaluation_lab(runs=None, retrieval_cases=None) -> dict:
    dialogue = evaluate_dialogue()
    integrated = evaluate_runs(runs)

    retrieval = {
        "evaluation_type": "retrieval",
        "status": "blocked",
        "reason": "No retrieval cases supplied.",
        "metrics": {},
        "cases": [],
    }
    if retrieval_cases:
        cases = [evaluate_case(case) for case in retrieval_cases]
        retrieval = {
            "evaluation_type": "retrieval",
            "status": "completed",
            "cases": cases,
            "metrics": {
                "mean_precision_at_k": sum(c["precision_at_k"] for c in cases) / len(cases),
                "mean_recall_at_k": sum(c["recall_at_k"] for c in cases) / len(cases),
                "mean_mrr": sum(c["mrr"] for c in cases) / len(cases),
            },
        }

    return {
        "schema_version": "evaluation-lab-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "evaluations": {
            "dialogue": dialogue,
            "retrieval": retrieval,
            "integrated": integrated,
        },
        "generation": {
            "status": "not_measured",
            "reason": "Generation quality requires actual model responses plus a declared judge or human review.",
        },
        "voice": {
            "status": "measured" if integrated.get("metrics", {}).get("voice_success_rate") is not None else "not_measured",
            "voice_success_rate": integrated.get("metrics", {}).get("voice_success_rate"),
        },
    }
