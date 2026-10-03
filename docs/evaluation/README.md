# Evaluation

Evaluation is a first-class component with explicit evidence classes.

## Deterministic dialogue

No model runtime required:

- state progression
- answer validation
- language routing
- session isolation
- intake completion

Run:

\`\`\`bash
python evaluation/run_baseline.py
\`\`\`

## Synthetic retrieval benchmark

Versioned fixtures validate the metric implementation without pretending that fixture output is live retrieval.

Metrics:

- Precision@K
- Recall@K
- MRR

Files:

\`\`\`
evaluation/retrieval_benchmark_v1.json
evaluation/run_retrieval_eval.py
\`\`\`

## Live retrieval evaluation

This executes the real local semantic-memory retrieval path using the configured Ollama embedding model:

\`\`\`bash
python -m evaluation.run_live_retrieval_eval \\
  --session-id demo \\
  --query "previous order" \\
  --relevant-id demo-1
\`\`\`

This is runtime-dependent integration evidence.

## Generation

The repository defines generation cases and scoring criteria in:

\`\`\`
evaluation/generation_benchmark_v1.json
\`\`\`

No generation-quality score is claimed until actual model responses are reviewed with a declared judge or human-review protocol.

## Voice and operations

Runtime evidence can report:

- TTS success
- voice latency
- total latency
- generation latency
- token usage when Ollama reports it
- stage-level failures

## Integrated Evaluation Lab

The product surface combines available evidence while preserving status:

- \`completed\`
- \`not_measured\`
- \`blocked\`

The browser therefore shows repository evidence even when a live runtime dataset is unavailable.

## Data policy

Benchmark fixtures are synthetic. No real patient or customer data belongs in them.
