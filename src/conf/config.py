from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    database_url: str
    secret_key: str

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"


settings = Settings()
