# Roadmap

## Current version — Local-first conversational AI system

The repository now uses Ollama for model inference and embeddings and a local JSON vector store for semantic memory.

### Completed engineering layers

1. Structured conversation and session state
2. Local LLM and embedding integration
3. Semantic memory and retrieval inspection
4. Run observability
5. Deterministic evaluation
6. Retrieval evaluation
7. Failure Observatory
8. Controlled experiments
9. Operations projection
10. Docker and CI/CD
11. Security baseline
12. Portfolio documentation

### Runtime verification milestone

The complete local runtime verification gate is now complete.

Verified:

1. Conversation and session continuity
2. Domain workflow routing and real `order_lookup` execution
3. Input and output policy enforcement
4. Controlled failure handling
5. Arabic session-language persistence and classification regression
6. Semantic memory persistence and retrieval

### Next development priorities

- add stronger automated integration tests around the verified runtime paths
- improve persistent/session storage boundaries
- measure real retrieval and generation behavior
- add authentication before any public deployment
