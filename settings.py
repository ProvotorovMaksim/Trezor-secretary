from pydantic_settings import BaseSettings
from os import getenv
import json

class Settings(BaseSettings):
    TELEGRAM_TOKEN: str = getenv("TOKEN", "your_token")
    GIGACHAT_CREDENTIALS: str = getenv("GIGACHAT_CREDENTIALS", "")
    DATABASE_URL: str = getenv("DATABASE_URL", "")
    DATABASE_DRIVER: str = getenv("DATABASE_DRIVER", "")
    POSTGRES_USER: str = getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = getenv("POSTGRES_DB", "")
    QDRANT_URL: str = getenv("QDRANT_URL", "")
    #QDRANT_API_KEY: str = getenv("QDRANT_API_KEY", "")

    class Config:
        env_file = ".env"

settings = Settings()
 