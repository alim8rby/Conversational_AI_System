# Portfolio Evidence Map

| Portfolio claim | Repository evidence |
|---|---|
| Stateful conversation | `interview_manager.py`, `agents/conversation_agent.py` |
| Local LLM and embeddings | `providers/ollama_client.py` |
| Semantic memory | `memory/memory_manager.py` |
| Memory inspection | `product/memory_inspector.py` |
| Reproducible evaluation | `evaluation/` |
| Failure analysis | `observability/`, `product/failure_observatory.py` |
| Controlled experiments | `experiments/` |
| Session-state product surface | `product/session_state.py` |
| Evaluation product surface | `product/evaluation_lab.py` |
| Operations surface | `product/operations.py` |
| Production hardening | `config/`, `app_health.py` |
| Security baseline | `docs/security.md`, `app.py` |
| CI/CD | `.github/workflows/ci.yml` |
| Containerization | `Dockerfile` |
| Browser demo | `static/index.html` |

## Evidence rule

Distinguish implemented code, deterministic evaluation, Ollama-dependent evaluation, and runtime verification. Never claim a metric without its corresponding evidence.
