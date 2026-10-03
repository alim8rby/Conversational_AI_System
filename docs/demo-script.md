# Portfolio Demo Script — ShopAssist

## 1. Start Ollama

Make sure the configured local models are available:

\`\`\`bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
\`\`\`

## 2. Index the reference domain

\`\`\`bash
python -m scripts.index_domain
\`\`\`

This builds the local vector store from the ShopAssist catalog, shipping, return, and FAQ knowledge.

## 3. Start the application

\`\`\`bash
python app.py
\`\`\`

Open \`http://localhost:8000\`.

## 4. Demonstrate the business path

Ask:

> What is the price of TrailRunner X1?

Then:

> What is the status of order ORD-1001?

The point is to show the path around the model:

\`\`\`text
request → workflow → authorized tool / knowledge → policy → response → run evidence
\`\`\`

## 5. Demonstrate the inspectability

Show:

- \`/session/<id>/state\`
- \`/session/<id>/memory?q=price\`
- \`/evaluation\`
- \`/failures\`
- \`/operations\`

The repository makes state, evidence, failures, and operational summaries inspectable instead of hiding them behind the chat UI.

## 6. Explain the evidence boundary

Use the labels deliberately:

- **completed** — executable or deterministic evidence exists
- **not_measured** — the evaluation protocol exists, but no scored runtime result is claimed
- **blocked** — required evidence is unavailable

The Evaluation Lab exposes the synthetic retrieval benchmark as repository evidence while keeping live retrieval and generation quality clearly separate.

## 7. Close

\`\`\`text
Build → Instrument → Evaluate → Observe failure → Experiment → Validate
\`\`\`

The portfolio story is the engineering system around a conversational model, not simply the model response.
