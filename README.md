# Conversational AI System

A local-first, stateful conversational AI application built to demonstrate the engineering around an AI system — not just the model response.

The system combines:

- structured multi-turn dialogue
- session state
- local LLM inference with Ollama
- local embeddings with Ollama
- session-scoped semantic memory
- retrieval inspection
- voice output
- run-level observability
- deterministic and retrieval evaluation
- failure analysis
- controlled experiments
- operations monitoring
- Docker and CI/CD
- baseline application security

## Architecture

```
Browser
   ↓
Flask API
   ↓
ConversationAgent
   ├── InterviewManager
   ├── OllamaClient → local LLM
   ├── MemoryManager → local semantic memory
   └── VoiceEngine
   ↓
Observability
   ├── Runs
   └── Failures
   ↓
Evaluation
   ├── Dialogue
   ├── Retrieval
   ├── Generation
   └── Voice
   ↓
Operations
```

The important design idea is the full engineering loop:

```
Build → Instrument → Evaluate → Observe Failure
                    ↓
             Experiment → Validate
```

## Local stack

| Layer | Technology |
|---|---|
| Application | Python 3.14.7, Flask |
| LLM | Ollama |
| Embeddings | Ollama |
| Semantic memory | Local JSON vector store |
| Voice | gTTS |
| Frontend | HTML / CSS / JavaScript |
| Container | Docker |
| CI | GitHub Actions |

No paid AI API or hosted vector database is required.

## Requirements

- Python 3.14.7
- Ollama
- Ollama models:
  - `llama3.2:3b`
  - `nomic-embed-text`

Install the models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Make sure Ollama is running.

## Run locally

Create and activate the Python 3.14.7 virtual environment. The repository includes a `.python-version` file so version-aware Python tooling can select the intended interpreter.

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Verify:

```bash
python --version
```

Expected:

```
Python 3.14.7
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Default configuration:

```text
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:3b
EMBED_MODEL=nomic-embed-text
MEMORY_STORE_PATH=data/memory.json
PORT=8000
```

Start the application:

```bash
python app.py
```

Open:

`http://localhost:8000`

## Product surfaces

| Endpoint | Purpose |
|---|---|
| `GET /` | Browser application |
| `GET /health` | Process health |
| `GET /ready` | Local AI readiness |
| `POST /chat` | Conversation |
| `GET /session/<id>/state` | Session progress |
| `GET /session/<id>/memory` | Memory inspection |
| `GET /evaluation` | Evaluation Lab |
| `GET /failures` | Failure Observatory |
| `GET /failures/<id>` | Failure detail |
| `GET /operations` | Operations snapshot |

## Evaluation

The repository distinguishes evidence types instead of inventing scores.

### Deterministic

Tests:

- state transitions
- answer validation
- language routing
- session isolation
- intake completion

Run:

```bash
python evaluation/run_baseline.py
```

### Retrieval

Metrics:

- Precision@K
- Recall@K
- MRR

The live retrieval evaluator uses the local Ollama embedding model and local memory store.

### Generation

Generation quality requires actual model outputs and a declared evaluation method.

### Voice

Voice evaluation requires actual TTS execution.

Unavailable evidence is represented as `blocked` or `not_measured`.

## Failure → Experiment → Validation

Failures are treated as engineering evidence.

A failure record can capture:

- what should have happened
- what actually happened
- evidence
- severity
- root-cause hypothesis
- linked experiment
- lifecycle status

Experiments then provide:

`Failure → Hypothesis → Intervention → Measurement → Decision`

The first registered experiment, EXP001, documents the correction of a language-routing problem where numeric content could incorrectly influence language detection.

## Repository structure

```
agents/              Conversation orchestration
config/              Configuration and validation
evaluation/          Evaluation engines and benchmarks
experiments/         Controlled experiment registry
memory/              Local semantic memory
observability/       Run and failure evidence
product/             Product-facing projections
providers/           Ollama integration
static/              Browser client
tests/               Automated tests
voice/               Text-to-speech
docs/                Architecture and engineering documentation
```

## Tests

```bash
python -m unittest discover -s tests -v
pytest -q
python -m compileall -q .
```

CI also builds the Docker image and runs `pip-audit`.

## Docker

The application container does not contain Ollama. Ollama remains a separate local service.

On Docker Desktop, the application can reach a host Ollama instance through the appropriate host gateway address, for example:

```text
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

The exact host networking configuration is environment-dependent.

## Security baseline

Implemented:

- request-size limits
- session/message limits
- generic client errors
- configurable CORS
- security response headers
- non-root Docker user
- environment-based configuration
- raw-input redaction by default
- read-only CI permissions
- dependency auditing

A public deployment would additionally require authentication, authorization, TLS, rate limiting, network controls, and production secret/logging management.

## Verification boundary

The repository is standardized on Python 3.14.7 across local development, CI, and Docker.

The project has been structurally refactored for the local-first stack, but the complete application has **not yet been runtime-verified locally**.

Do not interpret repository structure as proof of live model, retrieval, voice, Docker, or CI execution.

## Portfolio positioning

The project demonstrates:

> **How to build, inspect, evaluate, debug, and improve a stateful conversational AI system.**

It is intentionally more than a chatbot demo.

## Disclaimer

This is a technical conversational-AI demonstration. It is not a medical diagnostic system and should not be used as a substitute for professional clinical care.

## License

MIT.
