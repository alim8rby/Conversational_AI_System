# EXP001 — Script-Based Language Detection

## Objective

Eliminate false Arabic classifications for English messages containing digits without changing Arabic-script detection.

## Baseline

Commit: `a69d7d0e625dfae85ee2e58d4fa3361267416ef1` benchmark work, with the defect observed in B005.

Baseline rule:

```text
Arabic if Arabic script OR any digit is present
```

Observed:

| Input | Expected | Baseline |
|---|---|---|
| `I am 30 and work in finance.` | en | ar |
| `أنا عندي ثلاثين سنة` | ar | ar |

## Hypothesis

Language routing should use script evidence rather than the presence of digits.

## Intervention

Replace digit-based routing with:

```text
Arabic if Arabic Unicode script is present
Otherwise English
```

No model, prompt, retrieval, or state-machine changes were made.

## Validation

Deterministic cases checked against the changed implementation:

| Case | Expected | Observed |
|---|---|---|
| English + number | en | en |
| Arabic text | ar | ar |
| English without number | en | en |
| Arabic + number | ar | ar |

All four isolated checks passed.

## Result

B005's documented failure condition is resolved while the existing Arabic-script behavior remains intact.

## Limitation

A full repository test execution could not be performed in this environment because outbound GitHub access was unavailable. The validation above executes the exact changed function logic locally; the repository's full test suite should still be run in a network-enabled development environment.

## Decision

Keep the change. It is minimal, directly addresses a measured baseline defect, and does not alter unrelated behavior.

## Next experiment candidate

Instrument the next highest-impact risk rather than making another speculative optimization.
