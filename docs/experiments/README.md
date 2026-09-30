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
| EXP002 | Embedding-Based Intake Relevance | completed | Unreliable 3B binary relevance classification | controlled similarity separation | keep prototype threshold |

EXP001 documents the known language-routing correction. It is a controlled case result, not a claim of a fresh full-system benchmark run.

EXP002 documents the intake relevance redesign. Its 0.46 threshold is an initial empirical prototype boundary based on five relevant and five irrelevant controlled examples, not a production-calibrated classifier.
