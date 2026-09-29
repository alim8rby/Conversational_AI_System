# Run Observability Query Layer

The run store is the read-only evidence layer for persisted conversational runs.

## Run metadata

Each persisted run records reproducibility metadata without storing provider secrets:

- application version
- LLM model
- embedding model
- Pinecone index
- prompt version
- retrieval K
- generation temperature
- generation max tokens

It also records total end-to-end latency in addition to stage-level latency.

## Supported queries

- list all valid run records
- retrieve one run by run ID
- summarize total, successful, failed, and failure-rate counts

## Design

The query layer does not modify run records and does not change conversation behavior.

```text
Persisted Run JSON
       ↓
    RunStore
       ↓
 Run / Summary
       ↓
Operations UI / Failure Observatory
```

This layer intentionally stays small. More advanced aggregation should be added only when a concrete monitoring requirement is identified.
