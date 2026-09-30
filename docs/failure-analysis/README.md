# Failure Observatory

The Failure Observatory converts mismatches between expected and actual behavior into structured engineering evidence.

## Categories

- **Dialogue** — incorrect state transitions, validation, or clarification.
- **Retrieval** — missed or irrelevant memories.
- **Generation** — unsupported or contextually incorrect responses.
- **Voice** — synthesis or audio failures.
- **Infrastructure** — application or local-model service failures.

## Record

Each failure can contain:

- failure ID
- timestamp
- session ID
- category
- stage
- severity
- expected behavior
- actual behavior
- evidence
- root cause when known
- experiment ID when investigated
- lifecycle status

## Lifecycle

Observed → classify → evidence → hypothesis → experiment → change → re-evaluate.

Raw conversational content is not required for a failure record.
