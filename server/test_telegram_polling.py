import httpx
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    async with httpx.AsyncClient(timeout=40) as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching updates: {e}")
            return None


async def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file.")
        return

    print("--- Telegram Simple Receiver (Polling) ---")
    print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}")
    print("Waiting for messages... (Press Ctrl+C to stop)")

    offset = None
    while True:
        updates = await get_updates(offset)
        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                update_id = update["update_id"]
                offset = update_id + 1

                if "message" in update:
                    msg = update["message"]
                    chat = msg.get("chat", {})
                    user = msg.get("from", {})
                    text = msg.get("text", "No text")

                    print(f"\n[New Message]")
                    print(f"From: {user.get('first_name')} (@{user.get('username')})")
                    print(f"Chat ID: {chat.get('id')}")
                    print(f"Text: {text}")
                    print("-" * 20)

        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPolling stopped.")
