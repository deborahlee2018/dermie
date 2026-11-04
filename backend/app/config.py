from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    claude_api_key: str
    telegram_bot_token: str = ""  # optional until bot is set up

    class Config:
        env_file = ".env"


settings = Settings()
