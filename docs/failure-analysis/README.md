# Failure Observatory

## Purpose

The Failure Observatory turns individual system failures into structured engineering evidence. A failure is an observed mismatch between expected and actual system behavior.

## Failure taxonomy

| Category | Examples | Evidence |
|---|---|---|
| dialogue | wrong state transition, invalid answer accepted | expected vs actual state |
| retrieval | relevant memory missed, irrelevant memory ranked highly | relevant IDs vs ranked IDs |
| generation | unsupported answer, poor response quality | response + evaluation |
| voice | synthesis failure, missing audio | voice status + error |
| infrastructure | provider timeout, API failure | exception + latency |

## Failure record contract

Each recorded failure should contain:

- failure_id
- timestamp_utc
- session_id when applicable
- category
- stage
- severity
- expected_behavior
- actual_behavior
- evidence
- root_cause when known
- experiment_id when investigated
- status: open, investigating, resolved, or wont_fix

## Failure lifecycle

Observed failure → classify → capture evidence → form hypothesis → experiment → change → re-run benchmark → resolved or still failing.

## Rule

Every optimization should be traceable to a measured failure or a measurable product requirement. Do not create improvements without an evaluation target.
