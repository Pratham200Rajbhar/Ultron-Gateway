You are a senior Python engineer.

Build a lightweight Python FastAPI service that runs on a personal laptop and uses Ollama to generate text content.

SYSTEM ROLE:

- This service ONLY generates content.
- It receives prompts from a remote server and returns generated text.

FUNCTIONAL REQUIREMENTS:

1. Expose POST /generate endpoint.
2. Accept JSON input with a "prompt" field.
3. Validate a shared secret passed in HTTP header X-SECRET.
4. Call Ollama locally to generate text using a configurable model.
5. Return generated content as JSON.
6. Support long-running requests (up to 120 seconds).

TECHNICAL REQUIREMENTS:

- Python 3.10+
- FastAPI
- Ollama Python client
- Pydantic models
- Clear error messages

PROJECT STRUCTURE:
laptop/
├── app.py
├── ollama_client.py
├── models.py
├── config.py
└── requirements.txt

CONFIGURATION:

- OLLAMA_MODEL (default: llama3)
- SHARED_SECRET

DELIVERABLE:

- Provide complete runnable code
- Keep the code minimal
- No database
- No async queues
- No external dependencies beyond FastAPI and Ollama
