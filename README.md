# Conversational AI System

A local-first, stateful conversational AI application built to demonstrate the engineering around an AI system — not just the model response.

The reference product is **ShopAssist**, a configurable e-commerce assistant domain that exercises workflow routing, business knowledge, tool execution, policy enforcement, semantic memory, voice output, evaluation, observability, failure analysis, and operations.

## What the system demonstrates

- domain-configurable workflows
- policy and guardrail evaluation
- multi-turn conversation and explicit session lifecycle
- local LLM inference with Ollama
- local embeddings with Ollama
- session-scoped semantic memory
- knowledge retrieval
- controlled business-tool execution
- multilingual response language (\`en\` / \`ar\`)
- explicit-language TTS
- run-level observability
- structured failure records
- deterministic and synthetic evaluation
- live retrieval evaluation entry point
- operations monitoring
- Docker and CI/CD
- application security baseline

## Architecture

\`\`\`text
Browser
   ↓
Flask API
   ↓
ConversationAgent
   ├── PolicyEngine
   ├── WorkflowManager
   ├── ToolManager
   ├── OllamaClient → local LLM + embeddings
   ├── KnowledgeBase → domain retrieval
   ├── MemoryManager → session semantic memory
   └── VoiceEngine → explicit session language
   ↓
Run Evidence
   ├── Runs
   └── Failures
   ↓
Evaluation Lab
   ├── Deterministic dialogue
   ├── Synthetic retrieval
   ├── Runtime retrieval entry point
   └── Generation protocol
   ↓
Operations
\`\`\`

The core engineering loop is:

\`\`\`text
Build → Instrument → Evaluate → Observe Failure
                    ↓
             Experiment → Validate
\`\`\`

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
- \`llama3.2:3b\`
- \`nomic-embed-text\`

Install the models:

\`\`\`bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
\`\`\`

## Run locally

Create the environment and install dependencies:

\`\`\`bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
cp .env.example .env
\`\`\`

Verify the interpreter:

\`\`\`bash
python --version
\`\`\`

Expected:

\`\`\`text
Python 3.14.7
\`\`\`

Index the demo domain:

\`\`\`bash
python -m scripts.index_domain
\`\`\`

Start the application:

\`\`\`bash
python app.py
\`\`\`

Open:

\`\`\`text
http://localhost:8000
\`\`\`

## Portfolio demo

The intended demo is ShopAssist:

1. Ask: \`What is the price of TrailRunner X1?\`
2. Ask: \`What is the status of order ORD-1001?\`
3. Inspect \`/session/<id>/memory\`.
4. Open \`/evaluation\`.
5. Open \`/failures\` and \`/operations\`.

The point is to show the system around the model: domain retrieval, authorized tools, policy constraints, semantic memory, voice output, and persistent evidence.

See \`docs/demo-script.md\` for the full walkthrough.

## Product surfaces

| Endpoint | Purpose |
|---|---|
| \`GET /\` | Browser demo |
| \`GET /health\` | Process health |
| \`GET /ready\` | Ollama-backed readiness |
| \`POST /session/<id>/start\` | Start a session with \`en\` or \`ar\` |
| \`POST /chat\` | Conversation turn |
| \`GET /session/<id>/state\` | Session state |
| \`GET /session/<id>/memory\` | Semantic-memory inspection |
| \`GET /evaluation\` | Evaluation Lab |
| \`GET /failures\` | Failure Observatory |
| \`GET /failures/<id>\` | Failure detail |
| \`GET /operations\` | Operations snapshot |

## Evaluation

The repository separates evidence types rather than manufacturing scores.

### Deterministic

Run:

\`\`\`bash
python evaluation/run_baseline.py
\`\`\`

This covers dialogue-state behavior and other deterministic contracts.

### Synthetic retrieval

Run:

\`\`\`bash
python evaluation/run_retrieval_eval.py
\`\`\`

This evaluates metric calculation against the versioned synthetic fixture.

### Live retrieval

Run:

\`\`\`bash
python -m evaluation.run_live_retrieval_eval \\
  --session-id demo \\
  --query "previous order" \\
  --relevant-id demo-1
\`\`\`

This requires the local Ollama embedding runtime and actual memory records.

### Generation

Generation cases and rubrics exist, but no quality score is claimed until actual outputs are reviewed under a declared judge or human-review protocol.

### Evidence states

- \`completed\` — measured evidence exists
- \`not_measured\` — protocol exists but no measured result is claimed
- \`blocked\` — required runtime evidence is unavailable

## Observability and failure analysis

Every completed run is persisted locally. Recorded run errors are projected into \`FailureStore\` so failures become queryable product evidence instead of remaining only in logs.

The lifecycle is:

\`\`\`text
Run → Error → Failure record → Experiment → Validation
\`\`\`

Input is redacted from persisted run records by default.

## Docker

The image does **not** contain Ollama. Ollama remains a host-side service.

Docker Desktop example:

\`\`\`bash
docker build -t conversational-ai-system .
docker run --rm -p 8000:8000 \\
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \\
  conversational-ai-system
\`\`\`

The provided Dockerfile defaults \`OLLAMA_BASE_URL\` to \`http://host.docker.internal:11434\` for this local-demo pattern.

For Linux hosts, use the host networking/addressing mechanism appropriate to your environment; do not assume \`host.docker.internal\` is available everywhere.

## Runtime smoke test

With the application running:

\`\`\`bash
python -m scripts.runtime_smoke_test
\`\`\`

The smoke test checks health/readiness, starts a real ShopAssist session, sends a product question, verifies a non-empty business response, and reports the returned voice artifact.

## Configuration

The main runtime configuration lives in \`.env.example\`. Settings now cover the application, model runtime, domain pack, tool timeout, and observability directories.

\`\`\`text
OLLAMA_BASE_URL
LLM_MODEL
EMBED_MODEL
DOMAIN_CONFIG_PATH
MEMORY_STORE_PATH
TOOL_TIMEOUT_SECONDS
OBSERVABILITY_RUNS_DIR
OBSERVABILITY_FAILURES_DIR
\`\`\`

## Tests

\`\`\`bash
python -m unittest discover -s tests -v
pytest -q
python -m compileall -q .
\`\`\`

CI also builds the Docker image and runs \`pip-audit\`.

## Security baseline

Implemented:

- request-size limits
- strict session-ID format
- safe TTS output path construction
- message limits
- generic client errors
- configurable CORS
- security response headers
- non-root Docker user
- environment-based configuration
- raw-input redaction by default
- read-only CI permissions
- dependency auditing

A public deployment would additionally require authentication, authorization, TLS, rate limiting, network controls, centralized logging, durable shared state, secret management where secrets are introduced, and deployment-level container verification.

## Verification boundary

The repository documents local runtime verification separately from what is established by code and deterministic tests.

The portfolio-safe claims are:

- the architecture and product surfaces are implemented in the repository
- deterministic and synthetic evaluation are inspectable
- runtime-dependent evaluation has explicit entry points
- generation quality remains unscored unless real outputs are reviewed
- Docker-to-host Ollama is documented as a local-demo pattern, not a verified production deployment

## Repository structure

\`\`\`text
agents/              Conversation orchestration
config/              Configuration
domains/             Reference and test domain packs
evaluation/          Evaluation engines and benchmarks
experiments/         Controlled experiments
knowledge/           Domain RAG
memory/              Session semantic memory
observability/       Run and failure evidence
policies/            Policy engine
product/             Product-facing projections
providers/           Ollama integration
scripts/              Runtime and indexing utilities
static/              Browser demo
tests/               Automated tests
tools/               Business-tool registry and demo tools
voice/               Text-to-speech
workflows/           Workflow routing
docs/                Architecture and portfolio material
\`\`\`

## Portfolio positioning

> **A modular, local-first conversational AI system designed to be built, inspected, evaluated, debugged, and improved — not merely prompted.**

## Disclaimer

This is a technical conversational-AI demonstration. It is not a medical diagnostic system and should not be used as a substitute for professional clinical care.

## License

MIT.
