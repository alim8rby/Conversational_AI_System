# V1 System Blueprint — Conversational AI System

## 1. Purpose

Transform the existing conversational prototype into a measurable, reproducible conversational AI system suitable for an AI Engineer / Data Scientist portfolio.

The product remains a stateful conversational system with:

- structured intake
- multilingual interaction
- semantic session memory
- free-form dialogue
- text-to-speech output
- HTTP API
- browser client

The portfolio objective is not to add features indiscriminately. It is to demonstrate the full engineering loop:

**baseline → measurement → failure analysis → experiment → improvement → validation → deployment**

---

## 2. Current System

### Runtime flow

```text
Browser
   |
   v
Flask /chat
   |
   v
ConversationAgent
   |
   +--> InterviewManager
   |       |
   |       +--> in-memory session state
   |
   +--> Together AI
   |       |
   |       +--> embeddings
   |       +--> LLM classification
   |       +--> dialogue generation
   |
   +--> MemoryManager
   |       |
   |       +--> Together embeddings
   |       +--> Pinecone
   |
   +--> VoiceEngine
           |
           +--> gTTS
```

### Existing components

| Layer | Current implementation | Status |
|---|---|---|
| UI | `static/` browser client | Existing |
| API | Flask `app.py` | Existing |
| Orchestration | `ConversationAgent` | Existing |
| Dialogue state | `InterviewManager` | Existing |
| LLM | Together AI | Existing |
| Embeddings | Together AI | Existing |
| Vector memory | Pinecone | Existing |
| Voice | gTTS | Existing |
| Tests | unittest core tests | Existing |
| Containerization | Dockerfile | Existing |
| Evaluation | No reproducible benchmark | Gap |
| Observability | Basic Flask exception logging | Gap |
| Experiment tracking | Not implemented | Gap |
| Structured run data | Not implemented | Gap |

---

## 3. Target Architecture

```text
                    +----------------------+
                    |    Browser Client    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      API Layer       |
                    | validation / errors  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Conversation         |
                    | Orchestrator         |
                    +----+------------+----+
                         |            |
              +----------+            +-----------+
              v                                   v
     +------------------+                +------------------+
     | Dialogue State   |                | Memory /         |
     | Manager          |                | Retrieval        |
     +--------+---------+                +--------+---------+
              |                                   |
              +----------------+------------------+
                               |
                               v
                    +----------------------+
                    | Model / Prompt      |
                    | Runtime             |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Structured Response |
                    +----+------------+----+
                         |
               +---------+---------+
               v                   v
        +-------------+     +-------------+
        | Voice Layer |     | Evaluation  |
        +-------------+     | + telemetry |
                            +-------------+
```

### Architectural principle

Do not rewrite the working prototype. Introduce explicit contracts and measurement boundaries around it, then refactor only when evidence shows a need.

---

## 4. Product Surfaces

The final portfolio demonstration should expose six conceptual surfaces:

1. **Conversation** — normal user interaction.
2. **Session State** — current intake section, field, and completion status.
3. **Memory Inspector** — retrieved memories and relevance information.
4. **Evaluation Lab** — benchmark runs and metrics.
5. **Failure Observatory** — categorized failures and representative examples.
6. **Operations** — latency, errors, model/configuration, and run metadata.

These do not all need to be separate production UI pages. They define the evidence the repository must contain.

---

## 5. Data Contracts

The system should eventually record the following entities.

### Session

- session_id
- language
- created_at
- current_section
- current_field
- intake_complete

### Message

- session_id
- turn_id
- role
- text
- timestamp

### Retrieval Result

- session_id
- query
- memory_id
- rank
- similarity_score
- retrieved_text

### Model Run

- model
- embedding_model
- prompt_version
- temperature
- max_tokens
- latency
- token usage when available
- error status

### Evaluation Result

- benchmark_id
- run_id
- metric
- score
- expected
- observed

### Failure

- run_id
- category
- subtype
- severity
- input
- expected
- observed
- root-cause hypothesis

---

## 6. Evaluation Strategy

The first serious milestone is a deterministic benchmark rather than more features.

### A. Dialogue / state evaluation

Measure:

- expected next section
- expected next field
- state-transition accuracy
- intake completion rate
- invalid-answer handling
- clarification rate

### B. Retrieval evaluation

Create a small labeled conversation benchmark.

Measure:

- Recall@K
- Precision@K
- MRR
- nDCG
- irrelevant retrieval rate

### C. Generation evaluation

Measure:

- relevance
- contextual consistency
- response completeness
- unsupported-claim rate
- policy/guardrail adherence

### D. System evaluation

Measure:

- end-to-end latency
- model latency
- retrieval latency
- voice generation latency
- error rate
- successful response rate

### E. Reproducibility

Every benchmark run should record:

- model
- embedding model
- prompt version
- configuration
- test-set version
- timestamp
- random seed where applicable

---

## 7. Baseline Experiment

Before changing prompts, models, retrieval strategy, or architecture:

1. Freeze the current implementation as the baseline.
2. Build a small versioned benchmark.
3. Run the benchmark.
4. Record failures.
5. Establish baseline metrics.
6. Only then run optimization experiments.

This is the key transition from **"I built a chatbot"** to **"I engineered and evaluated a conversational AI system."**

---

## 8. Initial Failure Taxonomy

### Dialogue

- wrong state transition
- skipped field
- repeated field
- incorrect clarification
- premature intake completion

### Retrieval

- relevant memory missed
- irrelevant memory retrieved
- stale/duplicate memory
- poor ranking

### Generation

- ignores session context
- contradicts previous turn
- unsupported claim
- excessive verbosity
- incorrect language

### Voice

- synthesis failure
- language mismatch
- stale output file
- latency failure

### Infrastructure

- invalid request
- missing credentials
- provider failure
- timeout
- malformed model response

---

## 9. V1 Implementation Sequence

### Phase 1 — Baseline

- Add benchmark schema.
- Add deterministic test conversations.
- Add evaluation runner.
- Capture baseline metrics.
- Preserve current runtime behavior.

### Phase 2 — Instrumentation

- Add structured run/turn metadata.
- Capture retrieval scores.
- Capture latency.
- Capture model configuration.
- Capture failures without leaking secrets.

### Phase 3 — Failure Observatory

- Normalize failure taxonomy.
- Store representative failures.
- Produce error-analysis reports.
- Identify the highest-impact failure modes.

### Phase 4 — Experiments

Run controlled comparisons such as:

- current retrieval vs alternative retrieval strategy
- current top-k vs different top-k
- prompt version A vs B
- model A vs B
- context-window strategies

Each experiment must have a hypothesis, configuration, benchmark, metrics, and conclusion.

### Phase 5 — Productionization

- request validation
- persistent state boundaries
- provider abstraction where justified
- integration tests with mocks
- CI
- structured logging
- health checks
- deployment documentation

### Phase 6 — Portfolio Packaging

Final repository should communicate:

**Problem → Architecture → Baseline → Evaluation → Experiments → Improvements → Failure Analysis → Deployment → Results**

---

## 10. Current Findings

The existing implementation already demonstrates meaningful engineering:

- modular API/orchestration/state/memory/voice separation
- external LLM inference
- embedding-based semantic checks
- vector retrieval
- stateful multi-turn dialogue
- multilingual routing
- Docker packaging
- unit testing

The principal weaknesses are measurement and operational contracts rather than lack of AI functionality.

Notable technical risks to validate during baseline work:

1. `detect_language()` treats any digit as Arabic, which can misclassify otherwise English messages containing numbers.
2. Interview state is process-local, so state disappears on restart and is not shared across workers.
3. Conversation history is process-local and can grow without an explicit bound.
4. Pinecone retrieval returns text but currently discards similarity scores, preventing retrieval-quality measurement.
5. The prompt dataset under `prompts/` is not visibly part of the active runtime path and should be traced before being retained or removed.
6. Voice output uses a fixed session filename, so repeated turns overwrite the previous audio artifact.
7. `ConversationAgent` performs multiple external model calls inside a single interaction, making latency and failure attribution important.
8. There is no reproducible benchmark proving that semantic similarity + LLM classification improves intake handling.
9. Error handling converts several provider failures into generic responses without structured failure classification.

These are hypotheses/findings to validate with tests and instrumentation, not assumptions to blindly refactor around.

---

## 11. Definition of Portfolio-Ready

The project is ready for public presentation when a reviewer can answer all of these from the repository:

- What problem does the system solve?
- How does the architecture work?
- What was the baseline?
- How was quality measured?
- What failed?
- What experiment was run?
- What changed?
- Did the change measurably improve the system?
- What trade-offs were observed?
- How is the system tested?
- How can it be run?
- What would be built next?

The final LinkedIn post should emphasize measured engineering work rather than simply listing technologies.
