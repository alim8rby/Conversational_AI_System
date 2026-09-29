# Architecture

## Target architecture
Browser → API → Conversation Orchestrator → State/Memory/Retrieval → LLM → Structured Response → Voice → Observability/Evaluation.

## Existing system
Flask API, ConversationAgent, InterviewManager, Pinecone memory, Together AI, gTTS, browser client, Docker, and tests.

## Architectural principle
Preserve working components while introducing explicit contracts, evaluation, observability, and production boundaries incrementally.
