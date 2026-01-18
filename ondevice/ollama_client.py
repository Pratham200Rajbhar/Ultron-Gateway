import ollama
from config import settings


async def generate_text(prompt: str) -> str:
    """
    Generates text using the local Ollama service.
    """
    response = ollama.generate(
        model=settings.OLLAMA_MODEL,
        prompt=prompt,
    )
    return response["response"]
