# Memory Inspector

## Purpose

The Memory Inspector makes retrieval behavior inspectable without changing retrieval behavior or exposing vector values.

## API

`GET /session/<session_id>/memory?q=<query>&k=3`

The response uses `memory-inspector-v1` and includes:

- session ID
- query
- requested top-k
- retrieved count
- memory ID
- rank
- retrieval score
- retrieved text

Vector values are intentionally excluded.

## Architecture

```
Browser / evaluator
       |
       v
Memory Inspector API
       |
       v
MemoryManager.retrieve()
       |
       v
Pinecone
```

The inspector is read-only. It is an observability/product surface over the existing retrieval contract.

## Evaluation relationship

The inspector's memory IDs, ranks, and scores are the same evidence consumed by retrieval evaluation. This creates a traceable path:

`Query → Retrieved IDs → Rank/Score → Retrieval Metrics`

The synthetic retrieval benchmark validates the metric implementation; the inspector itself does not imply production retrieval quality.
