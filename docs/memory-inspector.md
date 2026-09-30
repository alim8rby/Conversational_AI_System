# Memory Inspector

The Memory Inspector makes local semantic retrieval visible without exposing embedding vectors.

## API

`GET /session/<session_id>/memory?q=<query>&k=3`

Returns:

- session ID
- query
- requested K
- retrieved count
- memory ID
- rank
- cosine similarity score
- retrieved text

## Architecture

```
Query
  ↓
Memory Inspector
  ↓
MemoryManager
  ↓
Ollama embeddings + local memory
```

The inspector is read-only and exposes the same memory IDs and rankings used by retrieval evaluation.
