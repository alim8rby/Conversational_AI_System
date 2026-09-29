# Evaluation

Evaluation is a first-class product component.

## Evaluation layers

1. **Deterministic dialogue** — state progression, validation, language routing, session isolation, and intake completion.
2. **Retrieval** — Precision@K, Recall@K, and MRR using synthetic fixtures and provider-backed live runs.
3. **Generation quality** — relevance, coherence, instruction adherence, groundedness, and unsupported-claim control.
4. **Voice and operations** — voice success, voice latency, total latency, generation latency, and token usage when available.
5. **Integrated evaluation** — combines measured evidence without silently treating unmeasured dimensions as passing.

## Evidence rules

- Deterministic scores may be produced locally without external providers.
- Provider-backed retrieval scores require a populated vector index.
- Generation scores require actual model responses plus a declared judge or human review.
- Voice scores require actual TTS execution.
- Missing measurements are recorded as blocked or not_measured, never as zero or pass.
- No real patient data belongs in benchmark fixtures.

## Result contract

evaluation/evaluation_schema_v1.json defines the common shape:

evaluation_id → benchmark_version → cases → metrics → failures

The goal is reproducibility and traceability rather than one opaque quality score.

## Current execution status

The repository contains the evaluation machinery for all defined dimensions. Provider-backed generation, retrieval, and voice results must still be executed in an environment with the required external services.
