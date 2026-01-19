from fastapi import FastAPI, Header, HTTPException, Depends, Request
from models import GenerateRequest, GenerateResponse
from ollama_client import generate_text
from config import settings
import logging
import time


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="On-Device Ollama Service")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method
    client_ip = request.client.host if request.client else "unknown"

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        status_code = response.status_code

        log_msg = f"Request: {method} {path} - Client: {client_ip} - Status: {status_code} - Time: {process_time:.2f}ms"
        if status_code >= 400:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"Request Error: {method} {path} - Client: {client_ip} - Error: {str(e)} - Time: {process_time:.2f}ms",
            exc_info=True,
        )
        raise


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
