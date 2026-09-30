# Experiment Registry

Experiments connect an observed problem to a hypothesis, intervention, measurable outcome, and decision.

## Lifecycle

Observed failure → objective → hypothesis → baseline → intervention → metric → result → decision

## Rules

1. Preserve the baseline.
2. Change one meaningful variable at a time where practical.
3. Define metrics before interpreting results.
4. Record blocked or inconclusive experiments.
5. Link experiments to failures when applicable.
6. Do not claim improvement without measurement.

## Current registry

| ID | Experiment | Status | Motivation | Metric | Decision |
|---|---|---|---|---|---|
| EXP001 | Script-Based Language Detection | completed | B005 language-routing failure | language detection accuracy | keep |

EXP001 documents the known language-routing correction. It is a controlled case result, not a claim of a fresh full-system benchmark run.
