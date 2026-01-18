from pydantic import BaseModel
from typing import Optional, List

# Telegram Models
class TelegramMessage(BaseModel):
    message_id: int
    text: Optional[str] = None
    chat: dict

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None

# Laptop Service Models
class LaptopRequest(BaseModel):
    prompt: str

class LaptopResponse(BaseModel):
    generated_content: str

# External API Models
class ExternalPostRequest(BaseModel):
    content: str

class ExternalPostResponse(BaseModel):
    status: str
    message: Optional[str] = None
