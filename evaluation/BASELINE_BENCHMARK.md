# Baseline Benchmark Specification

## Purpose

This benchmark evaluates the current conversational system before any optimization.

It is intentionally small, deterministic, versioned, and focused on measurable system behavior.

## Benchmark scope

V1 evaluates four dimensions:

1. Dialogue-state progression
2. Answer validation and clarification
3. Retrieval quality
4. End-to-end conversation behavior

Generation quality and latency will be added after the core benchmark contracts are established.

## Dataset design

Each benchmark case represents one controlled conversation.

### Case fields

- `case_id`: stable identifier
- `description`: what the case tests
- `language`: `en` or `ar`
- `turns`: ordered user inputs
- `expected_states`: expected state after each accepted answer
- `expected_clarifications`: turns expected to trigger clarification
- `tags`: failure-analysis categories

## V1 benchmark cases

### B001 — Normal English intake

Tests normal progression through the first intake fields.

Expected behavior:

- first user message is accepted
- state progresses from `personal_info/main`
- next state becomes `personal_info/additional_details`
- valid subsequent answer is accepted

Tags: `happy_path`, `en`

### B002 — Short invalid answer

Tests the deterministic answer validator.

Input examples:

- `k`
- `ha`

Expected behavior:

- answer is rejected
- clarification is returned
- intake state does not advance

Tags: `validation`, `clarification`, `en`

### B003 — Off-topic intake answer

Tests semantic relevance and LLM classification.

Example:

Question:
`Tell me a little about yourself, such as your age, occupation, and living situation.`

Answer:
`The weather has been strange today.`

Expected behavior:

- answer is rejected
- current state remains unchanged
- clarification is requested

Tags: `relevance`, `classification`

### B004 — Arabic intake

Tests Arabic interaction.

Expected behavior:

- Arabic input is detected as Arabic
- Arabic prompt is returned
- valid answer advances the state

Tags: `arabic`, `multilingual`

### B005 — English containing numbers

Tests a known language-detection risk.

Example:

`I am 30 and work in finance.`

Expected behavior:

- English should remain English
- system should not switch to Arabic solely because digits are present

Tags: `language_detection`, `known_risk`

### B006 — Clarification escalation

Tests repeated invalid/off-topic answers.

Expected behavior:

- first failure produces clarification 1
- second failure produces clarification 2
- third and subsequent failures use the final clarification style
- state does not advance until a valid answer is received

Tags: `clarification`, `state_integrity`

### B007 — Session isolation

Tests that two sessions do not share interview state.

Expected behavior:

- session A and session B maintain independent states
- answering in A must not advance B

Tags: `session_isolation`, `state`

### B008 — Intake completion

Tests the transition from structured intake to free-form conversation.

Expected behavior:

- all required fields can be completed
- `is_complete()` becomes true
- subsequent user input enters free-form generation

Tags: `state_transition`, `completion`

## Metrics

### 1. State Transition Accuracy

`correct_expected_state / total_evaluated_transitions`

Measures whether the system reaches the expected dialogue state.

### 2. Clarification Precision

Among turns expected to trigger clarification, measure how often clarification is actually returned.

### 3. Invalid Answer Rejection Rate

`correctly_rejected_invalid_answers / invalid_answers`

### 4. Session Isolation Rate

`isolated_sessions / tested_session_pairs`

Target for a correct implementation: 100%.

### 5. Language Detection Accuracy

`correct_language_predictions / language_test_cases`

### 6. Intake Completion Success

Fraction of complete benchmark conversations that successfully reach free-form mode.

## Retrieval benchmark

A separate retrieval fixture will contain:

- synthetic conversation memories
- query
- relevant memory IDs
- irrelevant memory IDs

For each query, the evaluator will calculate:

- Precision@K
- Recall@K
- MRR

This will initially test the retrieval component independently from the LLM.

## Evaluation principles

- No production credentials in benchmark files.
- No real patient data.
- No dependence on network services for deterministic state tests.
- Model-dependent tests must use mocks or explicit integration-test markers.
- Every benchmark result records the benchmark version.
- Baseline results must be preserved before optimization.

## Baseline record

Each baseline run should capture:

- git commit SHA
- benchmark version
- Python version
- model configuration
- embedding configuration
- metrics
- failures
- execution timestamp

## Success criterion

The benchmark itself is successful when another developer can clone the repository, run the deterministic tests, and reproduce the same state-machine results without the local Ollama runtime.

Ollama-dependent evaluation is a separate integration layer.
