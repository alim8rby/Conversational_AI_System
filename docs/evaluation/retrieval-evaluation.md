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
