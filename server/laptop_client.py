import httpx
from config import settings
from models import LaptopResponse


async def get_laptop_generation(prompt: str) -> str:
    headers = {"X-SECRET": settings.LAPTOP_SHARED_SECRET}
    payload = {"prompt": prompt}

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            settings.LAPTOP_API_URL, json=payload, headers=headers
        )
        response.raise_for_status()
        data = response.json()
        # Assuming the response matches our LaptopResponse model
        laptop_res = LaptopResponse(**data)
        return laptop_res.generated_content
