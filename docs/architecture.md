# System Architecture

## Runtime architecture

```
Browser
  ↓
Flask API
  ↓
ConversationAgent
  ├── PolicyEngine
  ├── WorkflowManager
  ├── ToolManager
  │     └── Domain Tool Registry
  ├── OllamaClient → local LLM + embeddings
  ├── KnowledgeBase → domain RAG
  │     ├── DocumentLoader
  │     ├── LocalVectorStore
  │     └── ContextBuilder
  ├── MemoryManager → session semantic memory
  └── VoiceEngine
  ↓
Run / Failure Evidence
  ↓
Evaluation / Operations
```

## Domain configuration

The core engine is domain-agnostic. The active domain pack defines:

- assistant identity and purpose
- knowledge sources
- workflows
- tools and their callable handlers
- business policies
- optional structured intake

The current reference domain is `demo_ecommerce`. It exists to exercise the engine's business workflow, retrieval, tool, policy, and observability boundaries without changing the core engine.

## Conversation lifecycle

Session initialization is explicit at the API boundary:

`POST /session/<id>/start` initializes the session. Subsequent `POST /chat` calls process conversation turns.

For domains with structured intake enabled, each answer is classified before the intake state advances. For the current demo e-commerce domain, intake is disabled, so a started session can immediately enter workflow routing.

## Request lifecycle

For the current domain-enabled runtime:

```
User request
    ↓
Input policy
    ↓
Workflow routing
    ↓
Tool authorization
    ↓
Tool execution
    ↓
Memory + domain retrieval
    ↓
LLM generation
    ↓
Output policy
    ↓
User response
```

Not every workflow requires every stage. The engine only executes capabilities required by the selected domain workflow.

## Knowledge retrieval

Domain documents are loaded and chunked by `DocumentLoader`, embedded through Ollama, and persisted in a local JSON vector store. `KnowledgeBase` retrieves the most relevant chunks, and `ContextBuilder` bounds the context passed to the model.

The repository includes a maintenance command:

```bash
python -m scripts.index_domain
```

This must be run before the first RAG-backed runtime test and whenever domain knowledge changes.

## Evidence principles

1. Measure behavior instead of assuming it works.
2. Keep unavailable measurements explicitly blocked or not measured.
3. Treat failures as evidence for controlled experiments.
4. Keep inspection surfaces read-only.
5. Redact conversational input from persisted runs by default.

## Design principle

The application is deliberately local-first. No paid AI provider or hosted vector database is required to develop or demonstrate the system.

The provider boundary is isolated in `providers/ollama_client.py`, so model infrastructure can be changed later without rewriting the application architecture.
