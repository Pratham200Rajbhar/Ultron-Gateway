from fastapi import FastAPI, HTTPException, Request
from models import TelegramUpdate
from laptop_client import get_laptop_generation
from poster import post_to_external_api
from telegram import send_telegram_message
from config import settings
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Send notification if chat id is configured
    if (
        settings.DEFAULT_CHAT_ID
        and settings.DEFAULT_CHAT_ID != "your_telegram_chat_id_here"
    ):
        try:
            await send_telegram_message(
                int(settings.DEFAULT_CHAT_ID),
                "🚀 Ultron Gateway is LIVE!\nWaiting for Telegram commands...",
            )
            logger.info(f"Startup notification sent to {settings.DEFAULT_CHAT_ID}")
        except Exception as e:
            logger.warning(f"Could not send startup notification: {e}")
    else:
        logger.info("Startup notification skipped (no chat ID configured)")
    yield


app = FastAPI(title="Telegram-LLM-Poster Gateway", lifespan=lifespan)


@app.post("/telegram/webhook")
async def telegram_webhook(update: TelegramUpdate):
    if not update.message or not update.message.text:
        return {"status": "ignored", "reason": "no text message"}

    chat_id = update.message.chat["id"]
    prompt = update.message.text

    logger.info(f"Received prompt from chat_id {chat_id}: {prompt}")

    try:
        # 1. Forward to laptop service
        generated_content = await get_laptop_generation(prompt)
        logger.info(f"Received generation from laptop service")

        # 2. Post to external API
        await post_to_external_api(generated_content)
        logger.info(f"Successfully posted to external API")

        # 3. Send confirmation back to Telegram
        await send_telegram_message(
            chat_id, "Processing complete! Your content has been posted successfully."
        )

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Optionally notify user about the error
        try:
            await send_telegram_message(
                chat_id, f"Oops! Something went wrong: {str(e)}"
            )
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}
