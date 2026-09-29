# System Architecture

## Frozen architecture

```text
Browser
  ↓
API
  ↓
Conversation Orchestrator
  ↓
State / Memory / Retrieval
  ↓
LLM
  ↓
Structured Response
  ↓
Voice
  ↓
Observability / Evaluation
```

## Runtime responsibilities

### API

Validates request boundaries, routes product surfaces, and keeps client-facing errors generic.

### Conversation Orchestrator

Coordinates intake state, answer validation, retrieval, generation, and run evidence.

### State

`InterviewManager` provides deterministic structured progression across defined sections and fields.

### Memory

`MemoryManager` stores and retrieves session-scoped semantic memories through Pinecone.

### LLM

Together AI provides language-model inference and embeddings.

### Voice

The voice layer converts generated responses into audio and records voice success/latency evidence.

### Evidence

Run and failure stores provide read-only evidence consumed by evaluation and operations.

## Product architecture

```text
Conversation
     │
     ├── Session State
     ├── Memory Inspector
     ├── Evaluation Lab
     ├── Failure Observatory
     └── Operations
```

These surfaces are projections over the same underlying evidence rather than independent implementations of system state.

## Design principles

1. Preserve the working core before refactoring it.
2. Separate conversation behavior from evidence collection.
3. Make evaluation evidence explicit.
4. Never convert unavailable measurements into zero.
5. Treat failures as inputs to controlled experiments.
6. Keep product inspection surfaces read-only.
7. Keep sensitive conversational data out of observability by default.
