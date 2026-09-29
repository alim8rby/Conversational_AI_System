# Operations UI

## Purpose

The Operations surface is a read-only operator view over measured system evidence.

## API

`GET /operations`

The response contract is `operations-v1` and combines:

- persisted run counts and success/failure rates
- mean total request latency when measured
- stage-level error counts
- failure counts by category, severity, stage, and lifecycle status
- dialogue, retrieval, generation, and voice evaluation status
- measured run success rate

Health and readiness remain separate:

- `GET /health`
- `GET /ready`

This keeps liveness/readiness semantics distinct from historical operational telemetry.

## Browser surface

The main browser client shows:

- run volume
- run success rate
- mean latency
- stage error count
- failure summary
- evaluation status

Values are rendered as unavailable rather than zero when evidence is absent.

## Boundary

Point 10 is observational only. Deployment, CI/CD, authentication, secret handling, and security controls are addressed in Point 11.
