import httpx
from config import settings
import re


async def get_jwt_token() -> str:
    """Authenticate with the API and get JWT token."""
    # Parse username and password from EXTERNAL_API_KEY (format: username:password)
    username, password = settings.EXTERNAL_API_KEY.split(":", 1)

    login_url = "https://www.prathamrajbhar.tech/api/login"
    login_payload = {"username": username, "password": password}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            login_url, json=login_payload, headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        data = response.json()
        return data.get("accessToken") or data.get("token")


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


async def post_to_external_api(content: str):
    """Post blog content to the external API after authenticating."""

    # Step 1: Get JWT token
    jwt_token = await get_jwt_token()

    # Step 2: Extract title from content (first line or first heading)
    lines = content.strip().split("\n")
    title = lines[0].strip("#").strip() if lines else "Generated Blog Post"

    # Generate excerpt (first 150 characters of content)
    excerpt = content[:150] + "..." if len(content) > 150 else content

    # Step 3: Prepare blog payload
    blog_payload = {
        "title": title,
        "slug": generate_slug(title),
        "content": content,
        "excerpt": excerpt,
        "tags": ["ai-generated", "telegram"],
        "published": True,
    }

    # Step 4: Post to blog API with JWT token
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(
            settings.EXTERNAL_API_URL, json=blog_payload, headers=headers
        )
        response.raise_for_status()
        return response.json()
