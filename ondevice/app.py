from fastapi import FastAPI, Header, HTTPException, Depends
from models import GenerateRequest, GenerateResponse
from ollama_client import generate_text
from config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="On-Device Ollama Service")


async def verify_secret(x_secret: str = Header(...)):
    if x_secret != settings.SHARED_SECRET:
        logger.warning(f"Unauthorized access attempt with secret: {x_secret}")
        raise HTTPException(status_code=403, detail="Invalid shared secret")
    return x_secret


@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest, _=Depends(verify_secret)):
    logger.info(f"Received generation request for prompt: {request.prompt[:50]}...")
    try:
        content = await generate_text(request.prompt)
        logger.info("Generation successful")
        return GenerateResponse(generated_content=content)
    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.OLLAMA_MODEL}
