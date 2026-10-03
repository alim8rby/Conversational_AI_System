# Product & Architecture Plan — Conversational AI System

## Product concept

The repository is a reusable conversational AI engine with **ShopAssist** as its concrete reference domain.

The system demonstrates engineering around a conversational model:

- explicit session lifecycle
- domain-configurable workflows
- retrieval-grounded business answers
- controlled tool execution
- policy enforcement
- session-scoped semantic memory
- multilingual response language
- voice output
- run-level observability
- structured failure evidence
- deterministic and runtime evaluation
- operational inspection surfaces

## Reference journey

\`\`\`text
Start session
    ↓
Ask about a product or policy
    ↓
Route to a domain workflow
    ↓
Retrieve knowledge / execute an authorized tool
    ↓
Generate response
    ↓
Persist evidence
    ↓
Inspect memory, evaluation, failures, operations
\`\`\`

## Reference workflows

| Workflow | Evidence path |
|---|---|
| Product question | knowledge retrieval + product_search |
| Order tracking | order_lookup |
| Return request | return-policy retrieval |
| General support | knowledge retrieval |

## Demo boundary

The current demo is local-first:

- Ollama runs as a separate service.
- Flask owns the conversational runtime.
- Local JSON storage makes evidence inspectable.
- The browser is an interaction surface, not a hidden evaluation harness.

## Portfolio message

The project is the engineering loop around a model:

**build → instrument → evaluate → observe → experiment → validate**
