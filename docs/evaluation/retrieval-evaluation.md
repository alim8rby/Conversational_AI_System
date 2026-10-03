# Retrieval Evaluation

## Purpose

The application uses local embeddings and a local vector store. Retrieval quality is evaluated independently from generation.

## Metrics

- **Precision@K** — relevant results among the top K.
- **Recall@K** — relevant results recovered within the top K.
- **MRR** — reciprocal rank of the first relevant result.

## Flow

`Query → Ollama embedding → local memory search → ranked memory IDs → metrics`

The synthetic benchmark validates metric calculations. Live evaluation uses `MemoryManager.retrieve()` and requires Ollama to be running with the configured embedding model.

A live score is only a system result when the relevant memory IDs have been independently established.


## Live retrieval evaluation

Run the live evaluator when Ollama is available:

```bash
python -m evaluation.run_live_retrieval_eval
```

This evaluator uses the real `nomic-embed-text` embedding model and a temporary local memory store containing synthetic, independently labeled memories. It reports Precision@3, Recall@3, and MRR for the measured retrieval results.

The live score is evidence about this embedding/retrieval configuration only. It should not be presented as a general benchmark for semantic search or as evidence of generation quality.
