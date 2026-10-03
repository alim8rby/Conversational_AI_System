# Production Hardening

The application includes a production-oriented local/container baseline. Remaining gaps are documented explicitly rather than treated as solved by configuration alone.

## Process model

The container runs Gunicorn rather than Flask's development server.

Default configuration:

- 1 worker
- 4 threads
- 120-second request timeout
- graceful shutdown timeout of 30 seconds
- stdout/stderr access and error logs

The application currently keeps conversation history and session language in process memory. Therefore the default worker count is intentionally **1**. Increasing `WEB_CONCURRENCY` before introducing an external session/state store can split a user's conversation across workers.

For multi-worker or horizontally scaled deployment, externalize session state and coordinate shared persistence first.

## Configuration

- Centralized environment configuration.
- Ollama URL and model configuration are validated.
- No hosted AI credentials are required.
- `PORT` is validated as a positive integer.
- Gunicorn process settings are configurable through environment variables.

## API boundaries

- Session IDs: maximum 128 characters.
- Messages: maximum 4,000 characters.
- Request body: maximum 16 KiB.
- Client errors remain generic.
- Observability input is redacted by default.
- CORS is explicitly configurable.

## Health and readiness

- `GET /health` is a lightweight liveness check.
- `GET /ready` validates required runtime configuration and verifies that the configured Ollama service is reachable.
- Container health uses the liveness endpoint so dependency outages do not cause unnecessary container restarts.

## Container

- Python 3.14.7 slim base image.
- Dependencies installed without pip cache.
- Application runs as a non-root user.
- Healthcheck is configured.
- Ollama remains an external service rather than being bundled into the application image.

## CI/CD

GitHub Actions currently:

- uses Python 3.14.7
- compiles Python sources
- runs the test suite
- builds the Docker image
- runs `pip-audit`
- uses read-only repository permissions

## Current production gaps

Before public production deployment, the following remain required:

1. Authentication and authorization for application and operational endpoints.
2. TLS termination.
3. Rate limiting / abuse protection.
4. External session/state storage for multi-worker or multi-instance deployment.
5. Durable shared storage for memory and operational evidence where required.
6. Centralized logging and alerting.
7. Network controls around Ollama.
8. External secret management where secrets are introduced.
9. Container/image vulnerability scanning and an image update policy.
10. Deployment-level verification of the Docker image and health/readiness behavior.

These are deployment requirements, not claims about the current local demo.
