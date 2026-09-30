# System Architecture

## Runtime architecture

```
Browser
  ↓
Flask API
  ↓
ConversationAgent
  ├── InterviewManager
  ├── Ollama LLM
  ├── Local Semantic Memory
  └── VoiceEngine
  ↓
Run / Failure Evidence
  ↓
Evaluation / Operations
```

## Components

- **Flask API** — request validation, explicit session start, and product endpoints.
- **ConversationAgent** — coordinates dialogue, classification, retrieval, generation, and evidence.
- **InterviewManager** — deterministic structured session state.
- **OllamaClient** — local model interface for chat and embeddings.
- **MemoryManager** — session-scoped semantic memory stored locally in JSON.
- **VoiceEngine** — text-to-speech output.
- **Observability** — persisted run and failure evidence.
- **Evaluation** — deterministic, retrieval, generation, voice, and integrated evaluation contracts.
- **Product projections** — Session State, Memory Inspector, Evaluation Lab, Failure Observatory, and Operations.

## Conversation lifecycle

Session initialization is explicit at the API boundary. `POST /session/<id>/start` initializes the deterministic intake state and stores the first awaited field. Subsequent `POST /chat` calls consume the user's answer for that exact awaited field before advancing to the next field.

This prevents the first user message from being discarded or accidentally treated as an answer to a later field.

## Design principle

The application is deliberately local-first. No paid AI provider or hosted vector database is required to develop or demonstrate the system.

The provider boundary is isolated in `providers/ollama_client.py`, so model infrastructure can be changed later without rewriting the application architecture.

## Evidence principles

1. Measure behavior instead of assuming it works.
2. Keep unavailable measurements explicitly blocked or not measured.
3. Treat failures as evidence for controlled experiments.
4. Keep inspection surfaces read-only.
5. Redact conversational input from persisted runs by default.
