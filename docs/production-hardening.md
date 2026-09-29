# Production Hardening

## Scope

Point 5 hardens the existing API without changing model or retrieval behavior.

### Configuration

- Centralized environment configuration in `config/settings.py`.
- Required provider credentials are validated by readiness checks.
- Numeric configuration such as `PORT` is validated.
- Provider-independent unit tests can load configuration without credentials.

### API boundaries

- `/chat` rejects missing session/message values.
- Session IDs are bounded to 128 characters.
- Messages are bounded to 4,000 characters.
- Flask request bodies are bounded to 16 KiB.
- Errors returned to clients remain generic while details are captured through application logging and run observability.

### Health and readiness

- `GET /health` verifies process-level health.
- `GET /ready` verifies required provider configuration and returns HTTP 503 when the application is not ready.

Health and readiness intentionally have different meanings: a running process can be healthy while not being ready to serve provider-backed traffic.

### Container

The Docker image runs the application as a non-root user.

### Privacy

Observability continues to redact raw user input by default. Production debugging should use identifiers, metrics, and controlled evidence rather than storing conversational content unnecessarily.

## Validation status

Production-hardening tests have been added for configuration validation and health/readiness behavior. Full repository execution is still not claimed in this environment because outbound GitHub DNS/network access remains unavailable.
