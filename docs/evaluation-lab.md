# Evaluation Lab

## Purpose

The Evaluation Lab is the unified product surface for inspecting evaluation
evidence across dialogue, retrieval, generation, voice, and integrated
operations.

## API

`GET /evaluation`

The response uses `evaluation-lab-v1` and includes:

- deterministic dialogue evaluation
- retrieval evaluation when cases are supplied
- integrated run metrics
- generation quality measurement status
- voice measurement status

## Evidence rules

The lab follows the evaluation layer's evidence policy:

- deterministic tests may report measured local results
- retrieval metrics require actual retrieval cases
- generation quality requires actual model outputs and a declared judge or human review
- voice metrics require actual TTS execution
- unavailable measurements are represented as `blocked` or `not_measured`
- missing evidence is never converted to zero

## Product relationship

```
Evaluation Engines
      |
      v
Evaluation Lab Projection
      |
      +----> API
      |
      +----> Browser status panel
      |
      +----> Future dashboard
```

The Evaluation Lab is read-only. It does not alter model, retrieval, or benchmark behavior.
