# Failure Observatory UI

## Product surface

The Failure Observatory exposes structured failure evidence through two read-only endpoints:

- `GET /failures`
- `GET /failures/<failure_id>`

The collection endpoint supports filters for:

- category
- stage
- severity
- status

## Summary

The product projection reports:

- total failures
- category counts
- stage counts
- severity counts
- lifecycle status counts

## Failure detail

A failure detail record retains:

- expected behavior
- actual behavior
- evidence
- run/session identifiers when available
- root cause when known
- linked experiment ID when applicable
- lifecycle status

## Product rule

The UI does not mutate failures. Investigation and resolution remain controlled engineering actions, preserving the evidence trail.

## Browser surface

The main browser client exposes a compact failure status indicator. A dedicated dashboard can consume the same API in a later operations/product iteration.
