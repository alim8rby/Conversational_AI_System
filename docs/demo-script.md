# Portfolio Demo Script

## 1. Start Ollama

Verify the local model service is running and the configured chat and embedding models are installed.

## 2. Start the application

```bash
python app.py
```

Open `http://localhost:8000`.

## 3. Demonstrate conversation

Complete several structured intake responses and show the session-progress indicator.

## 4. Demonstrate inspection

Use:

- `/session/<id>/state`
- `/session/<id>/memory?q=<query>`

Explain that state and retrieval are inspectable rather than hidden.

## 5. Demonstrate evaluation

Open `/evaluation` and distinguish measured evidence from blocked or unavailable measurements.

## 6. Demonstrate failures and operations

Open:

- `/failures`
- `/operations`

Explain the loop:

`failure → hypothesis → experiment → validation`

## 7. Close with the engineering story

The project is not only a chatbot. It is a local-first conversational AI system with state, memory, evaluation, observability, failure analysis, and operational surfaces.
