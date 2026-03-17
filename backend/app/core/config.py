from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    groq_api_key: str
    gemini_api_key: Optional[str] = None
    database_url: str
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env"}

settings = Settings()