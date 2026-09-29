# Portfolio Demo Script

## Objective

Demonstrate the system as an engineered conversational AI platform rather than only a chat interface.

## Demo sequence

### 1. Start with the architecture

Show the README architecture:

`Browser → API → Orchestrator → State/Memory/Retrieval → LLM → Voice → Observability/Evaluation`

Explain that the project is built around measurable system behavior.

### 2. Start a conversation

Use the browser and complete several structured intake responses.

Point out the session progress indicator.

### 3. Show Session State

Open:

`/session/<session_id>/state`

Show:

- current section
- current field
- completion rate
- field completion flags

Explain that the projection exposes state without exposing answer values.

### 4. Show Memory

Open:

`/session/<session_id>/memory?q=<query>`

Show:

- retrieved memory IDs
- ranking
- similarity scores
- contextual text

Explain that retrieval is inspectable rather than hidden inside the prompt.

### 5. Show Evaluation

Open:

`/evaluation`

Explain the distinction between:

- measured
- blocked
- not measured

Do not present blocked metrics as zeros.

### 6. Show failures

Open:

`/failures`

Show the failure taxonomy and evidence fields.

Explain:

`failure → hypothesis → experiment → validation`

### 7. Show operations

Open:

`/operations`

Show:

- run volume
- success rate
- latency
- stage errors
- evaluation status

### 8. Show engineering hardening

Briefly show:

- Dockerfile
- GitHub Actions CI
- security baseline
- readiness endpoint
- non-root container

### 9. Close with the engineering story

The key message:

> The project demonstrates the full loop from conversational behavior to measurement, failure analysis, controlled improvement, and operational readiness.
