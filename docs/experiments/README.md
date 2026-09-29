# Experiment Registry

Experiments are the controlled mechanism for improving the system. Each experiment must connect an observed problem to a hypothesis, intervention, measurable outcome, and decision.

## Required lifecycle

Observed failure → Objective → Hypothesis → Baseline → Intervention → Metrics → Result → Decision

## Rules

1. Preserve the baseline before changing behavior.
2. Change one meaningful variable at a time when practical.
3. Define the evaluation metric before interpreting the result.
4. Record blocked or inconclusive experiments rather than silently discarding them.
5. Link experiments to failure records when a failure motivated the work.
6. Do not call an optimization successful without measured evidence.

## Registry

| ID | Experiment | Status | Motivation | Metric | Decision |
|---|---|---|---|---|---|
| EXP001 | Script-Based Language Detection | completed | B005 language-routing failure | Language detection accuracy | keep |

## Experiment record

Each experiment should contain:

- experiment ID and title
- objective
- hypothesis
- baseline
- intervention
- metrics
- result
- decision
- status
- relevant failure IDs or benchmark cases
- implementation commit
