# Portfolio Evidence Map

| Portfolio claim | Repository evidence | Evidence type |
|---|---|---|
| Stateful conversation | \`agents/conversation_agent.py\`, \`product/session_state.py\` | implemented |
| Domain-configurable assistant | \`domains/demo_ecommerce/domain.json\`, \`domains/domain_config.py\` | implemented |
| Local LLM + embeddings | \`providers/ollama_client.py\` | implemented |
| Semantic memory | \`memory/memory_manager.py\`, \`knowledge/vector_store.py\` | implemented |
| Retrieval inspection | \`product/memory_inspector.py\` | implemented |
| Business tools | \`tools/demo_ecommerce.py\`, \`tools/tool_manager.py\` | implemented |
| Policy / guardrails | \`policies/policy_engine.py\` | implemented |
| Run observability | \`observability/run.py\`, \`observability/run_store.py\` | implemented |
| Failure evidence | \`observability/failure_from_run.py\`, \`observability/failure_store.py\` | implemented |
| Deterministic dialogue evaluation | \`evaluation/evaluate_dialogue.py\`, \`evaluation/run_baseline.py\` | deterministic |
| Synthetic retrieval benchmark | \`evaluation/retrieval_benchmark_v1.json\`, \`evaluation/run_retrieval_eval.py\` | synthetic |
| Live retrieval evaluation | \`evaluation/run_live_retrieval_eval.py\` | runtime-dependent |
| Generation benchmark rubric | \`evaluation/generation_benchmark_v1.json\` | protocol / not measured |
| Integrated evaluation | \`evaluation/integrated_eval.py\`, \`product/evaluation_lab.py\` | mixed |
| Operations surface | \`product/operations.py\` | implemented |
| Browser demo | \`static/index.html\` | implemented |
| Containerization | \`Dockerfile\`, \`.env.example\` | implemented |
| CI/CD | \`.github/workflows/ci.yml\` | implemented |
| Security baseline | \`docs/security.md\`, \`app.py\` | implemented |

## Final evidence rule

The repository deliberately distinguishes:

1. implemented architecture
2. deterministic tests
3. synthetic benchmark evidence
4. Ollama/TTS-dependent runtime evidence
5. generation quality that has not been scored

Every portfolio statement should point to the corresponding evidence class. Missing evidence is not a metric.
