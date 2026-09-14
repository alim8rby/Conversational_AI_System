# Conversational AI System

A portfolio-oriented conversational AI prototype combining structured dialogue, semantic memory, multilingual interaction, and voice output.

## Overview

This project explores how a stateful conversational agent can move from a structured intake flow into contextual free-form dialogue while preserving relevant session information.

### Stack

- **Python / Flask** — HTTP API and application layer
- **Together AI** — LLM inference and embeddings
- **Pinecone** — session-scoped vector memory
- **gTTS** — text-to-speech output
- **HTML/CSS/JavaScript** — lightweight browser client
- **Docker** — containerized deployment

## Architecture

```text
Browser Client
      │
      ▼
   Flask API
      │
      ▼
ConversationAgent
   ┌───┼────────────────┐
   │   │                │
   ▼   ▼                ▼
InterviewManager   Together AI   VoiceEngine
   │                   │
   ▼                   ▼
Session State      MemoryManager
                       │
                       ▼
                    Pinecone
```

## Core Flow

1. A client creates a session and sends a message to `/chat`.
2. The agent detects the interaction language.
3. During intake, `InterviewManager` advances through structured fields.
4. Candidate answers are checked for relevance using semantic similarity and LLM classification.
5. After intake, the agent switches to free-form dialogue.
6. Relevant previous exchanges are retrieved from Pinecone and supplied as context.
7. The response is returned as text and synthesized audio.

## Repository Structure

```text
.
├── agents/                  # Conversation agent
├── memory/                  # Vector memory integration
├── prompts/                 # Prompt/data resources
├── voice/                   # Text-to-speech integration
├── static/                  # Browser client
├── tests/                   # Core unit tests
├── app.py                   # Flask entry point
├── interview_manager.py     # Dialogue state machine
├── Dockerfile               # Container configuration
├── .env.example             # Environment configuration template
└── requirements.txt         # Runtime dependencies
```

## API

### `POST /chat`

Request:

```json
{
  "session": "demo-001",
  "message": "I have been feeling stuck at work."
}
```

Response:

```json
{
  "reply": "...",
  "audio": "/static/tts/demo-001.mp3"
}
```

## Configuration

Copy `.env.example` to `.env` and provide your credentials:

```bash
TOGETHER_API_KEY=your-key
PINECONE_API_KEY=your-key
```

Optional settings include the LLM model, embedding model, Pinecone index, and application port.

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The server listens on port `8000` by default.

## Run with Docker

```bash
docker build -t conversational-ai-system .
docker run --env-file .env -p 8000:8000 conversational-ai-system
```

## Testing

Run the core tests with Python's standard test runner:

```bash
python -m unittest discover -s tests -v
```

## Engineering Notes

The prototype deliberately separates the main responsibilities into an API layer, conversation orchestration, interview state management, semantic memory, and voice generation. This makes the system easier to test and extend than a single prompt-driven application.

The current implementation is designed as a demonstration of conversational AI engineering rather than a production service. It does not provide medical diagnosis or replace professional care.

## Roadmap

- Persist structured session state outside process memory
- Add robust memory evaluation and retrieval metrics
- Add integration tests with mocked model/vector services
- Improve authentication, rate limiting, and request validation
- Add structured logging and observability
- Add CI for tests and linting
- Evaluate response quality with a reproducible test set

## License

No open-source license is currently specified.
