# Evaluation

Evaluation is a first-class component of the system.

## Layers

1. **Deterministic dialogue** — state progression, validation, language routing, session isolation, and intake completion.
2. **Retrieval** — Precision@K, Recall@K, and MRR against the local semantic memory.
3. **Generation** — relevance, coherence, instruction adherence, groundedness, and unsupported-claim control.
4. **Voice and operations** — TTS success, latency, generation latency, total latency, and token usage when Ollama reports it.
5. **Integrated evaluation** — combines measured evidence without treating missing evidence as failure or success.

## Evidence rules

- Deterministic evaluation requires no model service.
- Retrieval evaluation requires Ollama's embedding model and actual memory records.
- Generation evaluation requires actual model responses plus a declared judge or human-review protocol.
- Voice evaluation requires actual TTS execution.
- Missing evidence is represented as `blocked` or `not_measured`, never zero.

No real patient data belongs in benchmark fixtures.
