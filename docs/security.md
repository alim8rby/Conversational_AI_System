# Security Baseline

## Implemented

- Secrets are supplied through environment variables; `.env` is ignored by Git.
- Provider credentials are required by readiness validation.
- Request body size is capped at 16 KiB.
- Session IDs are capped at 128 characters.
- Chat messages are capped at 4,000 characters.
- Client errors do not expose exception details.
- Observability stores raw user input only when explicitly enabled.
- Docker runs the application as a non-root user.
- CORS is configurable through `CORS_ORIGINS`.
- Responses include baseline browser security headers:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`
  - `Cache-Control: no-store`
- CI has read-only repository permissions and runs dependency auditing.

## Deployment requirements

The deployment environment should additionally provide:

1. TLS termination / HTTPS.
2. Secret management outside the repository.
3. Authentication and authorization for operational endpoints.
4. Network restrictions around provider and vector-database access.
5. Centralized logs with retention controls.
6. Rate limiting at the edge.
7. Dependency and base-image update policy.

The current demo does **not** claim that its operational endpoints are authenticated. That is a deliberate documented boundary rather than hidden security debt.

## Verification rule

Security controls are considered implemented only when their behavior is covered by tests or directly verified in the deployment environment. CI configuration is committed here, but runtime CI execution has not been locally verified in this workspace.
