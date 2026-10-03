# Security Baseline

## Implemented

- `.env` is ignored by Git.
- No AI provider credentials are required.
- Ollama runs as a local service and is configured through `OLLAMA_BASE_URL`.
- Request body size is capped at 16 KiB.
- Session IDs are capped at 128 characters.
- Chat messages are capped at 4,000 characters.
- Client errors do not expose exception details.
- Observability stores raw user input only when explicitly enabled.
- Docker runs the application as a non-root user.
- CORS is configurable through `CORS_ORIGINS`.
- Baseline browser security headers are applied.
- The container uses Gunicorn rather than Flask's development server.
- Readiness verifies reachability of the configured Ollama service.
- CI has read-only repository permissions and runs dependency auditing.

## Deployment requirements

For a public deployment, additionally provide TLS, authentication/authorization, rate limiting, centralized logging, network controls around the Ollama service, and dependency/base-image update policies.

The demo does not claim that operational endpoints are authenticated.

## Verification

Controls should be backed by automated tests or direct deployment verification. Repository configuration alone is not treated as runtime evidence.
