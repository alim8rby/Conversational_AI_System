# Conversational AI System

A portfolio-grade **stateful conversational AI system** built around structured dialogue, semantic memory, voice interaction, reproducible evaluation, failure analysis, experiments, and production-oriented observability.

The project is intentionally more than a chatbot demo: it demonstrates how to **design, measure, debug, and operate a conversational AI system**.

## What this project demonstrates

- Stateful conversation orchestration
- Structured intake and state transitions
- Multilingual interaction
- Session-scoped semantic memory
- Retrieval inspection and evaluation
- LLM generation
- Text-to-speech output
- Run-level observability
- Deterministic evaluation
- Failure taxonomy and evidence
- Controlled experiments
- Session-state product surface
- Memory Inspector
- Evaluation Lab
- Failure Observatory
- Operations UI
- Docker deployment
- CI/CD and dependency auditing
- Basic application security hardening

---

## Product Architecture

```text
                         Browser
                            │
                            ▼
                       Flask API
                            │
                            ▼
                 Conversation Orchestrator
                     │       │       │
                     ▼       ▼       ▼
                  State   Memory   Retrieval
                     │       │       │
                     └───────┼───────┘
                             ▼
                            LLM
                             │
                             ▼
                    Structured Response
                             │
                             ▼
                           Voice
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
        Observability                  Evaluation
              │                             │
              ▼                             ▼
      Failure Observatory             Evaluation Lab
              │                             │
              └──────────────┬──────────────┘
                             ▼
                       Operations UI
```

### Core technology

| Layer | Technology |
|---|---|
| Application | Python, Flask |
| LLM | Together AI |
| Embeddings | Together AI |
| Vector memory | Pinecone |
| Voice | gTTS |
| Frontend | HTML / CSS / JavaScript |
| Container | Docker |
| CI/CD | GitHub Actions |
| Evaluation | Python test/evaluation modules |

---

## System Flow

1. A client creates a session and sends a message.
2. The API validates request boundaries.
3. The conversation agent determines the current interaction state.
4. During structured intake, `InterviewManager` advances through defined sections and fields.
5. Candidate answers are checked for validity and relevance.
6. Once the structured flow is complete, the agent moves into contextual dialogue.
7. Relevant session-scoped memories are retrieved from Pinecone.
8. The LLM generates the response.
9. The response is converted to speech.
10. The run records latency, stage metrics, token usage, status, and errors.
11. Evaluation and failure layers consume that evidence without modifying the conversation itself.

---

# Product Surfaces

## 1. Conversation

The primary user experience:

`POST /chat`

Returns:

- response text
- generated audio path

## 2. Session State

`GET /session/<session_id>/state`

Exposes a safe read-only projection of:

- current section
- current field
- completed fields
- completion rate
- section progress

Answer values are not exposed through this product surface.

## 3. Memory Inspector

`GET /session/<session_id>/memory?q=<query>&k=<k>`

Shows:

- retrieved memory IDs
- ranks
- similarity scores
- retrieved text

This creates an inspectable bridge between semantic retrieval and evaluation.

## 4. Evaluation Lab

`GET /evaluation`

Unifies:

- deterministic dialogue evaluation
- retrieval evaluation when real cases are supplied
- integrated run metrics
- generation measurement status
- voice measurement status

The system explicitly distinguishes **measured**, **blocked**, and **not measured** evidence.

## 5. Failure Observatory

`GET /failures`

Supports filtering by:

- category
- stage
- severity
- status

Failures retain:

- expected behavior
- actual behavior
- evidence
- root cause when known
- experiment linkage
- lifecycle status

Individual evidence:

`GET /failures/<failure_id>`

## 6. Operations

`GET /operations`

Combines:

- run volume
- success/failure rate
- latency
- stage-level errors
- failure summaries
- evaluation status

Health and readiness remain separate:

- `GET /health`
- `GET /ready`

---

# Evaluation Philosophy

A major design principle is:

> **Do not turn missing evidence into a score of zero, and do not call an optimization successful without measurement.**

The system separates:

### Deterministic evaluation

Examples:

- state transitions
- invalid-answer handling
- language routing
- session isolation
- intake completion

### Retrieval evaluation

Metrics:

- Precision@K
- Recall@K
- MRR

### Generation evaluation

Requires actual model outputs plus an explicit judge or human-review protocol.

### Voice evaluation

Uses actual TTS execution metrics.

### Operational evaluation

Tracks:

- success/failure rate
- latency
- token usage when available
- voice success rate
- stage-level failures

---

# Failure → Experiment → Validation

The project treats failures as engineering evidence.

```text
Observed Failure
       │
       ▼
Classification
       │
       ▼
Evidence
       │
       ▼
Hypothesis
       │
       ▼
Controlled Experiment
       │
       ▼
Implementation Change
       │
       ▼
Re-run Evaluation
       │
       ├── validated
       └── still failing / inconclusive
```

The first registered controlled experiment is **EXP001 — Script-Based Language Detection**.

It addressed a language-routing failure where numeric content could incorrectly influence language detection.

The experiment is documented as a controlled case outcome rather than being presented as a full benchmark execution.

---

# Observability

Each persisted run can contain:

- run ID
- timestamp
- session ID
- status
- application/model metadata
- prompt version
- retrieval configuration
- generation configuration
- stage metrics
- total latency
- token usage when available
- errors

Raw user input is **not stored by default**.

---

# Production Hardening

Implemented:

- centralized configuration
- environment-based secrets
- readiness validation
- request-size limits
- session/message limits
- generic client-facing errors
- non-root Docker execution
- configurable CORS
- security response headers
- Docker healthcheck
- CI test execution
- Python compilation check
- Docker build in CI
- dependency audit with `pip-audit`

Deployment-level requirements that remain outside the demo repository include:

- HTTPS/TLS termination
- external secret management
- authentication/authorization
- edge rate limiting
- centralized production logging
- network policy
- dependency/base-image update policy

---

# Repository Structure

```text
.
├── agents/                  # Conversation orchestration
├── config/                  # Centralized configuration
├── evaluation/              # Evaluation engines and benchmarks
├── experiments/             # Controlled experiment registry
├── memory/                  # Pinecone semantic memory
├── observability/           # Run and failure evidence
├── product/                 # Product-facing projections
├── prompts/                 # Prompt resources
├── static/                  # Browser application
├── tests/                   # Application tests
├── voice/                   # Text-to-speech
├── .github/workflows/       # CI/CD
├── Dockerfile
├── app.py
├── interview_manager.py
├── requirements.txt
└── .env.example
```

---

# API Surface

| Endpoint | Purpose |
|---|---|
| `GET /` | Browser application |
| `GET /health` | Process health |
| `GET /ready` | Provider readiness |
| `POST /chat` | Conversation |
| `GET /session/<id>/state` | Session state |
| `GET /session/<id>/memory` | Memory inspection |
| `GET /evaluation` | Evaluation Lab |
| `GET /failures` | Failure Observatory |
| `GET /failures/<id>` | Failure detail |
| `GET /operations` | Operations snapshot |

---

# Running Locally

## Requirements

- Python 3.11
- Together AI credentials
- Pinecone credentials
- a configured Pinecone index

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure:

```text
TOGETHER_API_KEY=...
PINECONE_API_KEY=...
PINECONE_INDEX=conversation-memory
```

Run:

```bash
python app.py
```

Default port:

```text
8000
```

## Docker

```bash
docker build -t conversational-ai-system .
docker run --env-file .env -p 8000:8000 conversational-ai-system
```

## Tests

```bash
python -m unittest discover -s tests -v
```

CI additionally runs:

```bash
pytest -q
python -m compileall -q .
pip-audit
docker build
```

---

# Project Roadmap

The system was developed in twelve controlled phases:

| Phase | Result |
|---:|---|
| 1 | Complete Observability |
| 2 | Complete Evaluation |
| 3 | Actual Failure Observatory |
| 4 | Controlled Experiments |
| 5 | Production Hardening |
| 6 | Session State Product Layer |
| 7 | Memory Inspector |
| 8 | Evaluation Lab |
| 9 | Failure Observatory UI |
| 10 | Operations UI |
| 11 | Deployment / CI/CD / Security |
| 12 | Portfolio Packaging & Demo |

All twelve phases are now structurally complete.

---

# Evidence and Verification Boundary

This repository distinguishes **implemented artifacts** from **runtime-verified measurements**.

The current development environment could inspect and modify the GitHub repository but could not establish outbound GitHub DNS/network connectivity for a full local execution cycle.

Therefore this project does **not** fabricate:

- fresh benchmark scores
- provider-backed retrieval scores
- generation-quality scores
- live latency measurements
- successful CI execution claims

Where evidence is unavailable, the system reports `blocked` or `not_measured`.

That distinction is part of the engineering design.

---

# Portfolio Positioning

This project demonstrates a broader AI-engineering workflow:

```text
Build
  ↓
Instrument
  ↓
Evaluate
  ↓
Observe failures
  ↓
Experiment
  ↓
Harden
  ↓
Operate
  ↓
Package
```

The main portfolio value is therefore not simply **"I built a chatbot."**

It is:

> **I built a stateful conversational AI system and an engineering framework around it for evaluation, observability, failure analysis, experimentation, and operational monitoring.**

---

## Disclaimer

This is a technical conversational-AI demonstration. It is not a medical diagnostic system and should not be used as a substitute for professional clinical care.

## License

MIT license is currently specified.
