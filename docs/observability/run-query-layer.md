# Run Observability

The run store is the read-only evidence layer for conversational turns.

## Recorded metadata

- application version
- LLM model
- embedding model
- local memory store
- prompt version
- retrieval K
- generation temperature
- generation max tokens

Stage and total latency are recorded when available.

## Query layer

`RunStore` supports listing runs, retrieving a run by ID, and summary statistics.

```
Persisted Run JSON
       ↓
    RunStore
       ↓
Operations / Failure Observatory
```

Raw user input is redacted by default. Enable `OBSERVABILITY_STORE_INPUT=true` only for controlled local debugging.
