"""Evaluation helpers for voice and operational run metrics."""

def evaluate_voice_run(run: dict) -> dict:
    voice = run.get("metrics", {}).get("voice", {})
    return {
        "voice_success": voice.get("voice_success"),
        "voice_latency_ms": voice.get("voice_latency_ms"),
        "status": "measured" if "voice_success" in voice else "not_measured",
    }

def evaluate_operational_run(run: dict) -> dict:
    metrics = run.get("metrics", {})
    generation = metrics.get("generation", {})
    return {
        "total_latency_ms": metrics.get("total_latency_ms"),
        "generation_latency_ms": generation.get("generation_latency_ms"),
        "total_tokens": generation.get("token_usage", {}).get("total_tokens"),
        **evaluate_voice_run(run),
    }
