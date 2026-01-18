import httpx
from config import settings


async def post_to_external_api(content: str):
    headers = {"Authorization": f"Bearer {settings.EXTERNAL_API_KEY}"}
    payload = {"content": content}

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            settings.EXTERNAL_API_URL, json=payload, headers=headers
        )
        response.raise_for_status()
        return response.json()
