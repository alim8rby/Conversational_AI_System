# Production Hardening

The application includes baseline hardening for a local AI service.

## Configuration

- Centralized environment configuration.
- Ollama URL and model configuration are validated.
- No hosted AI credentials are required.
- `PORT` is validated as a positive integer.

## API boundaries

- Session IDs: maximum 128 characters.
- Messages: maximum 4,000 characters.
- Request body: maximum 16 KiB.
- Client errors remain generic.
- Observability input is redacted by default.

## Health

- `GET /health` checks process health.
- `GET /ready` checks required local AI configuration.

## Container

The Docker image runs as a non-root user.

## Remaining deployment concerns

For a real public deployment, add authentication/authorization, TLS, rate limiting, external secret management where needed, centralized logging, network policy, and an update policy for dependencies and base images.
