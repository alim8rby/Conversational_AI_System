# Retrieval Evaluation

## Purpose

The conversational system retrieves memories from a vector store, but retrieval quality was not previously measurable. This layer establishes a provider-independent evaluation contract before connecting the evaluator to live Pinecone results.

## Metrics

- Precision@K: relevant results among the top K retrieved results.
- Recall@K: relevant results recovered within the top K divided by all relevant results.
- MRR: reciprocal rank of the first relevant result, averaged across queries.

## Evaluation flow

Query → Retriever → Ranked memory IDs → Retrieval evaluator → Precision@K / Recall@K / MRR

## V1 fixture

The synthetic fixture validates the metric implementation and evaluation contract. It is not evidence of production retrieval quality.

## Next integration step

Wire the same evaluator to MemoryManager.retrieve(), preserve memory_id and rank, and record the real provider/model/index configuration. Only provider-backed runs should be reported as system retrieval results.
