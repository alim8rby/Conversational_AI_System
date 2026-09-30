# Operations

The Operations surface is a read-only view over measured system evidence.

## API

`GET /operations`

It reports:

- run volume
- success/failure rate
- mean latency when measured
- stage-level errors
- failure summaries
- evaluation status

Health and readiness remain separate:

- `GET /health`
- `GET /ready`

Unavailable measurements are represented explicitly rather than as zero.
