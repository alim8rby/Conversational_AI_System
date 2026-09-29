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


## Executable comparison layer

The registry is backed by `experiments/registry.json` and validated by
`experiments/experiment_registry.py`.

`experiments/experiment_runner.py` compares explicitly supplied measured
baseline and intervention metrics. For numeric metrics it computes:

```
delta = intervention - baseline
```

Missing measurements produce `delta: null`; they are never treated as zero.

### Controlled experiment contract

Every completed experiment should make these artifacts discoverable:

1. baseline behavior or metric
2. intervention behavior or metric
3. metric definition
4. evidence reference
5. implementation change
6. decision
7. validation status

Provider-backed experiments remain blocked until the corresponding external
services are available and the evaluation is actually executed.

## EXP001

EXP001 is registered as the first completed controlled experiment. Its
documented B005 case changed from failure under the old language-routing rule
to success under script-based routing. This is a controlled case outcome,
not a claim that the entire repository benchmark was executed in the current
environment.
