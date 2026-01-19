import ollama
from config import settings
import time


async def generate_text(prompt: str) -> str:
    """
    Generates text using the local Ollama service.
    """
    print(f"DEBUG: Starting Ollama generation with model: {settings.OLLAMA_MODEL}")
    start = time.time()
    response = ollama.generate(
        model=settings.OLLAMA_MODEL,
        prompt=prompt,
    )
    duration = time.time() - start
    print(f"DEBUG: Ollama generation finished in {duration:.2f}s")
    return response["response"]
