from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    LAPTOP_API_URL: str
    LAPTOP_SHARED_SECRET: str
    EXTERNAL_API_URL: str
    EXTERNAL_API_KEY: str
    DEFAULT_CHAT_ID: str = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
