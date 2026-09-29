# Portfolio Evidence Map

| Portfolio claim | Repository evidence |
|---|---|
| Stateful conversation | `interview_manager.py`, `agents/conversation_agent.py` |
| Semantic memory | `memory/memory_manager.py` |
| Memory inspection | `product/memory_inspector.py` |
| Reproducible evaluation | `evaluation/` |
| Failure analysis | `observability/failure_store.py`, `product/failure_observatory.py` |
| Controlled experiments | `experiments/` |
| Session-state product surface | `product/session_state.py` |
| Evaluation product surface | `product/evaluation_lab.py` |
| Operations product surface | `product/operations.py` |
| Production hardening | `config/`, `app_health.py`, `docs/production-hardening.md` |
| Security baseline | `docs/security.md`, `app.py`, `.env.example` |
| CI/CD | `.github/workflows/ci.yml` |
| Containerization | `Dockerfile` |
| Browser demo | `static/index.html` |

## Evidence rule

Portfolio descriptions should distinguish between:

- implemented code
- documented architecture
- deterministic local evaluation
- provider-dependent evaluation
- runtime verification

Never claim a metric or deployment result without the corresponding evidence.
