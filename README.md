# WsS AI

**The Witnessing Soul System** — an experimental multilingual conversational AI built around structured interviewing, retrieval memory, and voice interaction.

## Overview

WsS AI explores how a conversational agent can combine a structured intake flow with free-form dialogue while maintaining session context.

The prototype currently integrates:

- **LLM conversation:** Together AI with Llama 3.1 8B Instruct Turbo
- **Structured interview:** progressive collection of user information across defined sections
- **Answer validation:** lightweight semantic similarity and LLM-based relevance checks
- **Session memory:** Pinecone vector retrieval scoped by session
- **Bilingual interaction:** English and Arabic input detection
- **Voice output:** text-to-speech responses
- **Web API:** Flask backend with a simple browser frontend
- **Containerization:** Docker-based deployment setup

## Architecture

```text
Browser / Client
      │
      ▼
   Flask API
      │
      ▼
ConversationAgent
   ┌───┼───────────────┐
   │   │               │
   ▼   ▼               ▼
InterviewManager   LLM / Together   VoiceEngine
   │                   │
   ▼                   ▼
Session State      MemoryManager
                       │
                       ▼
                    Pinecone
```

## Repository Structure

```text
.
├── agents/                  # Conversation agent logic
├── memory/                  # Vector memory integration
├── prompts/                 # Prompt resources
├── voice/                   # Text-to-speech integration
├── static/                  # Frontend assets and generated audio
├── app.py                   # Flask application entry point
├── interview_manager.py     # Structured interview state machine
├── test_together.py         # Basic model/API test
├── Dockerfile               # Container configuration
└── requirements.txt         # Python dependencies
```

## Core Flow

1. A client starts a session and sends a message to `/chat`.
2. The agent determines the interaction language.
3. During intake, the `InterviewManager` advances through structured fields.
4. Answers are checked for relevance before being recorded.
5. After intake, the agent switches to free-form conversation using session context and retrieved memory.
6. The response is synthesized into audio and returned alongside the text response.

## Example API

### `POST /chat`

```json
{
  "session": "demo-001",
  "message": "I have been feeling stuck at work."
}
```

Example response:

```json
{
  "reply": "...",
  "audio": "/static/tts/demo-001.mp3"
}
```

## Configuration

Set the required API credentials as environment variables before running the application:

```bash
export TOGETHER_API_KEY="your-key"
export PINECONE_API_KEY="your-key"
```

The Pinecone index configured by the current application is `wss-ai-memory`.

## Running Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The application runs on port `8000` by default.

## Docker

```bash
docker build -t wss-ai .
docker run --env TOGETHER_API_KEY="your-key" --env PINECONE_API_KEY="your-key" -p 8000:8000 wss-ai
```

## Project Status

This repository is an **experimental prototype**, not a production clinical system. It is intended to demonstrate conversational AI architecture, stateful dialogue, retrieval-augmented memory, multilingual interaction, and voice interfaces.

## Future Improvements

- Persist conversation content alongside vector embeddings for meaningful retrieval
- Improve session persistence and concurrency handling
- Add automated tests for interview progression and validation
- Separate configuration from application code
- Add structured logging and error handling
- Add evaluation datasets and response-quality metrics
- Harden deployment and security for production environments

## License

No open-source license is currently specified.
