from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    groq_api_key: str
    gemini_api_key: str
    database_url: str
    upload_dir: str = "uploads"

    class Config:
        env_file = ".env"

settings = Settings()