You are a senior backend engineer.

Build a Python FastAPI backend that acts as a controller between Telegram, a laptop-based LLM service, and an external posting API.

SYSTEM ROLE:

- This service does NOT generate content.
- It only routes requests and posts results.

FUNCTIONAL REQUIREMENTS:

1. Expose a POST /telegram/webhook endpoint compatible with Telegram Bot webhooks.
2. Parse incoming Telegram messages as plain text commands.
3. Forward the message text as a prompt to a remote laptop service via HTTP POST.
4. The laptop service URL must be configurable via environment variable LAPTOP_API_URL.
5. Wait for the laptop response (can take up to 120 seconds).
6. Extract generated content from the laptop response.
7. Post the generated content to an external API using HTTP POST.
8. External API URL and API key must come from environment variables.
9. Send a confirmation message back to Telegram after posting.

TECHNICAL REQUIREMENTS:

- Use Python 3.10+
- Use FastAPI
- Use requests or httpx
- Use Pydantic models
- Include proper error handling and timeouts
- Use a shared secret header (X-SECRET) when calling the laptop service

PROJECT STRUCTURE:
server/
├── main.py
├── telegram.py
├── laptop_client.py
├── poster.py
├── models.py
├── config.py
└── requirements.txt

CONFIGURATION:

- TELEGRAM_BOT_TOKEN
- LAPTOP_API_URL
- LAPTOP_SHARED_SECRET
- EXTERNAL_API_URL
- EXTERNAL_API_KEY

DELIVERABLE:

- Provide complete runnable code
- Keep the design simple and readable
- No database
- No background workers
- Synchronous request flow

IMPORTANT:

- Assume this is a personal tool
- No multi-user logic
- No scaling concerns
