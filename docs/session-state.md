# Session State Product Layer

## Purpose

The Session State surface exposes structured conversation progress without exposing stored answer values.

## Contract

`GET /session/<session_id>/state`

Returns `session-state-v1` with:

- session ID
- lifecycle status
- completed/total fields
- completion rate
- current section and field
- per-section completion
- per-field completion flags

Answer content is intentionally excluded from this projection.

## Product behavior

The browser client displays a compact session-progress indicator while the conversation continues.

## Architecture

```
InterviewManager
      |
      v
Session State Projection
      |
      +----> GET /session/:id/state
      |
      +----> Browser Session Inspector
```

The projection is read-only. Future product surfaces can consume the same contract without coupling themselves to the internal `InterviewManager.sessions` structure.
